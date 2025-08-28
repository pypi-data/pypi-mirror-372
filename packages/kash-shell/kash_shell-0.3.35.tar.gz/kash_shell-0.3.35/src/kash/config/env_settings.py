from clideps.env_vars.env_enum import EnvEnum


class KashEnv(EnvEnum):
    """
    Environment variable settings for kash. None are required, but these may be
    used to override default values.
    """

    KASH_LOG_LEVEL = "KASH_LOG_LEVEL"
    """The log level for console-based logging."""

    KASH_WS_ROOT = "KASH_WS_ROOT"
    """The root directory for kash workspaces."""

    KASH_GLOBAL_WS = "KASH_GLOBAL_WS"
    """The global workspace directory."""

    KASH_SYSTEM_LOGS_DIR = "KASH_SYSTEM_LOGS_DIR"
    """The directory for system logs."""

    KASH_SYSTEM_CACHE_DIR = "KASH_SYSTEM_CACHE_DIR"
    """The directory for system cache (caches separate from workspace caches)."""

    KASH_SHOW_TRACEBACK = "KASH_SHOW_TRACEBACK"
    """Whether to show tracebacks on actions and commands in the shell."""

    KASH_USER_AGENT = "KASH_USER_AGENT"
    """The user agent to use for HTTP requests."""
