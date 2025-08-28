from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from prettyfmt import fmt_path

from kash.config.logger import get_logger, reset_rich_logging
from kash.config.settings import (
    GLOBAL_WS_NAME,
    global_settings,
    resolve_and_create_dirs,
)
from kash.config.text_styles import STYLE_HINT
from kash.file_storage.metadata_dirs import MetadataDirs
from kash.model.params_model import GLOBAL_PARAMS, RawParamValues
from kash.shell.output.shell_output import PrintHooks, cprint
from kash.utils.errors import FileNotFound, InvalidInput, InvalidState
from kash.utils.file_utils.ignore_files import IgnoreFilter, is_ignored_default
from kash.workspaces.workspace_dirs import (
    check_strict_workspace_name,
    is_global_ws_dir,
    is_ws_dir,
)
from kash.workspaces.workspace_registry import WorkspaceInfo, get_ws_registry

if TYPE_CHECKING:
    from kash.file_storage.file_store import FileStore

log = get_logger(__name__)


class Workspace(ABC):
    """
    A workspace is the context for actions and is tied to a folder on disk.

    This is a minimal base class for use as a context manager. Most functionality
    is still in `FileStore`.

    Workspaces may be detected based on the current working directory or explicitly
    set using a `with` block:
    ```
    ws = get_ws("my_workspace")
    with ws:
        # code that calls current_ws() will use this workspace
    ```
    """

    @property
    @abstractmethod
    def base_dir(self) -> Path:
        """The base directory for this workspace."""


def resolve_ws(name: str | Path) -> WorkspaceInfo:
    """
    Parse and resolve the given workspace path or name and return a tuple containing
    the workspace name and a resolved directory path.

    "example" -> "example", Path("example")  [if example already exists]
    "/path/to/example" -> "example", Path("/path/to/example")
    "." -> "current_dir", Path("/path/to/current_dir") [if cwd is /path/to/current_dir]
    """
    if not name:
        raise InvalidInput("Workspace name is required.")

    name_str = str(name).strip().rstrip("/")

    if isinstance(name, Path):
        # Absolute paths respected otherwise relative to workspace root.
        if name.is_absolute():
            resolved = name
            parent_dir = resolved.parent
        else:
            parent_dir = global_settings().ws_root_dir
            resolved = parent_dir / name
    elif name_str.startswith(".") or name_str.startswith("/"):
        # Explicit paths respected otherwise use workspace root.
        resolved = Path(name_str).resolve()
        parent_dir = resolved.parent
        name = resolved.name
    else:
        parent_dir = global_settings().ws_root_dir
        resolved = parent_dir / Path(name_str)

    ws_name = check_strict_workspace_name(resolved.name)

    return WorkspaceInfo(ws_name, resolved, is_global_ws_dir(resolved))


def get_ws(name_or_path: str | Path, auto_init: bool = True) -> FileStore:
    """
    Get a workspace by name or path. Adds to the in-memory registry so we reuse it.
    With `auto_init` true, will initialize the workspace if it is not already initialized.
    """
    if isinstance(name_or_path, Path):
        name_or_path = name_or_path.expanduser().absolute()
    name = Path(name_or_path).name
    name = check_strict_workspace_name(name)
    info = resolve_ws(name_or_path)
    if not is_ws_dir(info.base_dir) and not auto_init:
        raise FileNotFound(f"Not a workspace directory: {fmt_path(info.base_dir)}")

    ws = get_ws_registry().load(info.name, info.base_dir, info.is_global_ws)
    return ws


@cache
def global_ws_dir() -> Path:
    kb_path = resolve_and_create_dirs(global_settings().global_ws_dir, is_dir=True)
    log.debug("Global workspace path: %s", kb_path)
    return kb_path


def get_global_ws() -> FileStore:
    """
    Get the global_ws workspace.
    """
    return get_ws_registry().load(GLOBAL_WS_NAME, global_ws_dir(), True)


def _switch_ws_settings(base_dir: Path) -> FileStore:
    """
    Switch the current workspace to the given directory.
    Updates logging and cache directories to be within that workspace.
    Does not reload the workspace if it's already loaded.
    """
    from kash.media_base.media_tools import reset_media_cache_dir
    from kash.web_content.file_cache_utils import reset_content_cache_dir

    info = resolve_ws(base_dir)
    ws_dirs = MetadataDirs(base_dir=info.base_dir, is_global_ws=info.is_global_ws)

    # Use the global log root for the global_ws, and the workspace log root otherwise.
    reset_rich_logging(None, info.name if not info.is_global_ws else None)

    if info.is_global_ws:
        # If not in a workspace, use the global cache locations.
        reset_media_cache_dir(global_settings().media_cache_dir)
        reset_content_cache_dir(global_settings().content_cache_dir)
    else:
        reset_media_cache_dir(ws_dirs.media_cache_dir)
        reset_content_cache_dir(ws_dirs.content_cache_dir)

    return get_ws_registry().load(info.name, info.base_dir, info.is_global_ws)


def current_ws(silent: bool = False) -> FileStore:
    """
    Get the current workspace based on the current working directory.
    Loads and registers the workspace if it is not already loaded.

    As a convenience, this call also auto-updates logging and cache directories
    if this has changed.
    """
    from kash.exec.runtime_settings import current_ws_context

    ws_context = current_ws_context()
    base_dir = ws_context.current_ws_dir
    if not base_dir:
        raise InvalidState(
            f"No workspace found in: {fmt_path(Path('.').absolute(), resolve=False)}\n"
            "Create one with the `workspace` command."
        )

    ws = _switch_ws_settings(base_dir)

    if not silent:
        did_log = ws.log_workspace_info(once=True)
        if did_log and ws.is_global_ws and not ws_context.override_dir:
            PrintHooks.spacer()
            log.warning("Note you are currently using the default global workspace.")
            cprint(
                "Create or switch to another workspace with the `workspace` command.",
                style=STYLE_HINT,
            )

    return ws


def current_ignore() -> IgnoreFilter:
    """
    Get the current ignore filter.
    """
    try:
        return current_ws().is_ignored
    except InvalidState:
        return is_ignored_default


T = TypeVar("T")


def ws_param_value(param_name: str, type: type[T] = str) -> T | None:
    """
    Get a global parameter value, checking if it is set in the current workspace first.
    """
    try:
        params = current_ws().params.get_raw_values()
    except InvalidState:
        params = RawParamValues()

    return params.get_parsed_value(param_name, type=type, param_info=GLOBAL_PARAMS)
