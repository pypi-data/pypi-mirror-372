import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from prettyfmt import fmt_lines, fmt_path

from kash.config.logger import get_logger
from kash.config.settings import atomic_global_settings, global_settings
from kash.model.items_model import Item
from kash.model.media_model import MediaType
from kash.model.paths_model import StorePath
from kash.utils.common.url import Url
from kash.utils.errors import FileNotFound, InvalidInput
from kash.utils.file_utils.file_formats_model import detect_media_type
from kash.web_content.canon_url import canonicalize_url
from kash.web_content.local_file_cache import CacheResult, Loadable, LocalFileCache

log = get_logger(__name__)


# Simple global cache for misc use. No expiration.
_global_content_cache = LocalFileCache(global_settings().content_cache_dir)

_content_cache = _global_content_cache


def reset_content_cache_dir(path: Path):
    """
    Reset the current content cache directory, if it has changed.
    """
    with atomic_global_settings().updates() as settings:
        current_cache_dir = settings.content_cache_dir

        if current_cache_dir != path:
            settings.content_cache_dir = path
            global _content_cache
            _content_cache = LocalFileCache(global_settings().content_cache_dir)
            log.info("Using web cache: %s", fmt_path(path))


def cache_file(
    source: Url | Path | Loadable, global_cache: bool = False, expiration_sec: float | None = None
) -> CacheResult:
    """
    Return a local cached copy of the item. If it is an URL, content is fetched.
    If it is a Path or a Loadable, a cached copy is returned.
    LocalFileCache uses httpx so httpx.HTTPError is raised for non-2xx responses.

    Uses the current content cache unless there is no current cache or `global_cache` is True,
    in which case the global cache is used.
    """
    cache = _global_content_cache if global_cache else _content_cache
    return cache.cache(source, expiration_sec)


def cache_api_response(
    url: Url,
    global_cache: bool = False,
    expiration_sec: float | None = None,
    parser: Callable[[str], Any] = json.loads,
) -> tuple[Any, bool]:
    """
    Cache an API response. By default parse the response as JSON.
    """
    cache = _global_content_cache if global_cache else _content_cache
    result = cache.cache(url, expiration_sec)
    parsed_result = parser(result.content.path.read_text())
    return parsed_result, result.was_cached


def cache_resource(
    item: Item, global_cache: bool = False, expiration_sec: float | None = None
) -> dict[MediaType, Path]:
    """
    Cache a resource item for an external local path or a URL, fetching or
    copying as needed and returning direct paths to the cached content.
    For media this may yield more than one format.
    """
    from kash.exec.preconditions import is_resource
    from kash.media_base.media_services import is_media_url
    from kash.media_base.media_tools import cache_media

    if not is_resource(item):
        raise ValueError(f"Item is not a resource: {item}")

    path: Path | None = None
    results: dict[MediaType, Path] = {}
    cache_result: CacheResult | None = None

    # Cache the content using media or content cache.
    if item.url:
        if is_media_url(item.url):
            results = cache_media(item.url)
        else:
            cache_result = cache_file(item.url, global_cache, expiration_sec)
    elif item.external_path:
        ext_path = Path(item.external_path)
        if not ext_path.is_file():
            raise FileNotFound(f"External path not found: {ext_path}")
        cache_result = cache_file(ext_path, global_cache, expiration_sec)
    elif item.original_filename:
        orig_path = Path(item.original_filename)
        if not orig_path.is_file():
            raise FileNotFound(f"Original filename not found: {orig_path}")
        cache_result = cache_file(orig_path, global_cache, expiration_sec)
    else:
        raise ValueError(f"Item has no URL or external path: {item}")

    if cache_result:
        path = cache_result.content.path

    # If we just have the local file path, determine its format.
    if not results and path:
        results = {detect_media_type(path): path}

    log.message(
        "Cached resource %s:\n%s",
        item.as_str_brief(),
        fmt_lines(
            f"{media_type.value}: {fmt_path(media_path)}"
            for media_type, media_path in results.items()
        ),
    )

    return results


def get_url_html(
    item: Item, global_cache: bool = False, expiration_sec: float | None = None
) -> tuple[Url | StorePath, str]:
    """
    Returns the HTML content of an URL item, using the content cache,
    or the body of the item if it has a URL and HTML body.
    """
    from kash.exec.preconditions import has_html_body, is_url_resource

    if is_url_resource(item) and item.url and not item.has_body:
        # Need to fetch the content.
        locator = Url(canonicalize_url(item.url))
        path = cache_file(locator, global_cache, expiration_sec).content.path
        with open(path) as file:
            html_content = file.read()
    else:
        if not item.body or not has_html_body(item):
            raise InvalidInput("Item must be a URL resource or have an HTML body")
        if not item.store_path:
            raise InvalidInput("Item missing store path")
        html_content = item.body
        locator = StorePath(item.store_path)

    return locator, html_content
