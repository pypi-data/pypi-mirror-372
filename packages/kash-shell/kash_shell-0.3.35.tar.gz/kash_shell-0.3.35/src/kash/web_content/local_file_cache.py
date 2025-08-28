import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from funlog import log_if_modifies
from prettyfmt import fmt_path
from strif import atomic_output_file, copyfile_atomic

from kash.utils.common.url import (
    Url,
    is_file_url,
    is_url,
    is_valid_path,
    normalize_url,
    parse_file_url,
)
from kash.utils.errors import FileNotFound
from kash.utils.file_utils.file_formats_model import file_format_info
from kash.utils.file_utils.filename_parsing import parse_file_ext
from kash.web_content.dir_store import DirStore
from kash.web_content.web_fetch import HttpHeaders, download_url

log = logging.getLogger(__name__)

_normalize_url = log_if_modifies(level="info")(normalize_url)


def read_mtime(path: Path) -> float:
    """
    Modification time for a file, or 0 if file doesn't exist or is not readable.
    """
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = 0
    return mtime


TIMEOUT = 30


class WebCacheMode(Enum):
    LIVE = 1
    TEST = 2
    UPDATE = 3


class InvalidCacheState(RuntimeError):
    pass


DEFAULT_SUFFIX = ""


@dataclass(frozen=True)
class Loadable:
    """
    An item that can be loaded and then cached to a file.
    """

    key: str
    """
    The unique identifier for the item. Used when creating unique cache filenames,
    as is or with added suffixes.
    """

    save: Callable[[Path], None]
    """
    Method that saves the item to the given path. Caller will handle path selection
    and atomicity of file creation. Raise an exception if the item cannot be saved.
    """


Cacheable = Url | Path | Loadable
"""
An item that can be cached as a file.
"""


@dataclass(frozen=True)
class CacheContent:
    """
    An item in the local file cache. If it was a cache miss for a web-fetched URL,
    also has HTTP headers.
    """

    path: Path
    headers: HttpHeaders | None


@dataclass(frozen=True)
class CacheResult:
    content: CacheContent
    was_cached: bool


def _suffix_for(cacheable: Cacheable) -> str | None:
    key = cacheable.key if isinstance(cacheable, Loadable) else cacheable

    # Check for recognized file extensions on URLs and Paths.
    filename_ext = parse_file_ext(str(key))
    if filename_ext:
        return filename_ext.dot_ext

    # Handle local paths
    if is_file_url(str(key)):
        path = parse_file_url(str(key))
    elif is_valid_path(str(key)):
        path = Path(str(key))
    else:
        # A non-local path with no recognized extension.
        return None

    # If it's a local file, check the file content too.
    file_ext = file_format_info(path).suggested_file_ext
    return file_ext.dot_ext if file_ext else None


def _key_for(cacheable: Cacheable) -> str:
    if isinstance(cacheable, Loadable):
        return cacheable.key
    elif isinstance(cacheable, str) and is_url(cacheable):
        return _normalize_url(cacheable)
    elif isinstance(cacheable, Path):
        return str(cacheable)
    else:
        raise ValueError(f"Invalid cacheable: {cacheable!r}")


class LocalFileCache(DirStore):
    """
    Storage and caching of local copies of web contents, other local files, or
    values (like results of calculations or API calls) in a simple directory
    structure.

    The LocalFileCache is a DirStore with a loading and caching mechanism based on a
    fixed object expiration time. Fetch timestamp is the modification time on
    file. Thread safe since file creation is atomic.

    Works on URLs, file:// URLs, local paths, and arbitrary Loadable objects
    that load or compute a value that can be saved to a file.

    Supports a backup/restore mechanism to/from an S3 bucket. Supply `backup_url`
    to use backup/restore.
    """

    # TODO: We don't fully handle fragments/sections of larger pages. It'd be preferable to extract
    # the part of the page at the anchor/fragment, but for now we ignore fragments and fetch/use
    # the whole page.
    # TODO: Consider saving HTTP headers as well.

    ALWAYS: float = 0
    NEVER: float = -1

    def __init__(
        self,
        root: Path,
        default_expiration_sec: float = NEVER,
        mode: WebCacheMode = WebCacheMode.LIVE,
        backup_url: Url | None = None,
    ) -> None:
        """
        Expiration is in seconds, and can be NEVER or ALWAYS.
        """
        super().__init__(root)
        self.default_expiration_sec = default_expiration_sec
        # In case we want to cache a few types of files in the future.
        self.folder = "originals"
        self.mode = mode
        self.backup_url = backup_url

        if backup_url and mode in (WebCacheMode.TEST, WebCacheMode.UPDATE):
            self._restore(backup_url)

    def _load_source(self, source: Cacheable) -> CacheContent:
        """
        Load or compute the given source and save it to the cache.
        """
        if self.mode == WebCacheMode.TEST:
            raise InvalidCacheState("_load_source called in test mode")

        # Get cache key and target path.
        key = _key_for(source)
        suffix = _suffix_for(source)
        cache_path = self.path_for(key, folder=self.folder, suffix=_suffix_for(source))

        headers = None
        if isinstance(source, Path) or (isinstance(source, str) and is_file_url(source)):
            # Local file or file:// URL.
            url_or_path = source
            if isinstance(url_or_path, Path):
                file_path = url_or_path
            else:
                parsed = parse_file_url(url_or_path)  # Raises ValueError if not a file URL.
                file_path = parsed
            if not file_path.exists():
                raise FileNotFound(f"File not found: {file_path}")
            log.info(
                "Copying local file to cache: %s -> %s", fmt_path(file_path), fmt_path(cache_path)
            )
            copyfile_atomic(file_path, cache_path, make_parents=True)
        elif isinstance(source, str) and is_url(source):
            # URL.
            url = _normalize_url(source)
            log.info("Downloading to cache: %s -> %s", url, fmt_path(cache_path))
            headers = download_url(url, cache_path)
            log.debug("Response headers: %s", headers)
        elif isinstance(source, Loadable):
            # Arbitrary loadable. Load and save (atomically).
            with atomic_output_file(
                cache_path, tmp_suffix=suffix or ".tmp", make_parents=True
            ) as tmp_path:
                source.save(tmp_path)
            if not cache_path.exists():
                # The source should have raised an exception if it failed to save.
                raise InvalidCacheState(
                    f"Loadable source failed to save to cache: {source}: {cache_path}"
                )
        else:
            raise ValueError(f"Invalid source: {source}")

        return CacheContent(cache_path, headers)

    def _age_in_sec(self, cache_path: Path) -> float:
        now = time.time()
        return now - read_mtime(cache_path)

    def _is_expired(self, cache_path: Path, expiration_sec: float | None = None) -> bool:
        if self.mode in (WebCacheMode.TEST, WebCacheMode.UPDATE):
            return False

        if expiration_sec is None:
            expiration_sec = self.default_expiration_sec

        if expiration_sec == self.ALWAYS:
            return True
        elif expiration_sec == self.NEVER:
            return False

        return self._age_in_sec(cache_path) > expiration_sec

    def is_cached(self, source: Cacheable, expiration_sec: float | None = None) -> bool:
        if expiration_sec is None:
            expiration_sec = self.default_expiration_sec

        key = _key_for(source)
        suffix = _suffix_for(source)
        cache_path = self.find(key, folder=self.folder, suffix=suffix)

        return cache_path is not None and not self._is_expired(cache_path, expiration_sec)

    def cache(self, source: Cacheable, expiration_sec: float | None = None) -> CacheResult:
        """
        Returns cached download path of given URL and whether it was previously cached.
        For file:// URLs does a copy.
        """
        key = _key_for(source)
        suffix = _suffix_for(source)
        cache_path = self.find(key, folder=self.folder, suffix=suffix)

        if cache_path and not self._is_expired(cache_path, expiration_sec):
            log.info("URL in cache, not fetching: %s: %s", key, fmt_path(cache_path))
            return CacheResult(CacheContent(cache_path, None), True)
        else:
            log.info("Caching new copy: %s", key)
            return CacheResult(self._load_source(source), False)

    def backup(self) -> None:
        if not self.backup_url:
            raise InvalidCacheState("Backup called without backup_url")
        self._backup(self.backup_url, self.folder)

    def backup_all(self) -> None:
        if not self.backup_url:
            raise InvalidCacheState("Backup called without backup_url")
        self._backup(self.backup_url, "")

    def restore(self) -> None:
        if not self.backup_url:
            raise InvalidCacheState("Restore called without backup_url")
        self._restore(self.backup_url, self.folder)

    def restore_all(self) -> None:
        if not self.backup_url:
            raise InvalidCacheState("Restore called without backup_url")
        self._restore(self.backup_url, "")
