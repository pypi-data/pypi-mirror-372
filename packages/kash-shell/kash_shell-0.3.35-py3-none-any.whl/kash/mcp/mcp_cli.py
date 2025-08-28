"""
Command-line launcher for running an MCP server. With no options, by default runs in
stdio standalone mode, with all kash tools exposed. But can be run in SSE standalone
mode or as a stdio proxy to another SSE server.
"""

import argparse
import logging
import os
from pathlib import Path

from clideps.utils.readable_argparse import ReadableColorFormatter

from kash.config.settings import (
    DEFAULT_MCP_SERVER_PORT,
    LogLevel,
    atomic_global_settings,
    global_settings,
)
from kash.config.setup import kash_setup
from kash.config.warm_slow_imports import warm_slow_imports
from kash.shell.version import get_version

__version__ = get_version()

DEFAULT_PROXY_URL = f"http://localhost:{DEFAULT_MCP_SERVER_PORT}/sse"

MCP_CLI_LOG_PATH = global_settings().system_logs_dir / "mcp_cli.log"


log = logging.getLogger()


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=ReadableColorFormatter)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--workspace",
        default=global_settings().global_ws_dir,
        help=f"Set workspace directory. Defaults to kash global workspace directory: {global_settings().global_ws_dir}",
    )
    parser.add_argument(
        "--proxy",
        action="store_true",
        help="Run in proxy mode, expecting kash to already be running in SSE mode on another local process",
    )
    parser.add_argument(
        "--proxy_url",
        type=str,
        help=(
            "URL for proxy mode. If you are running kash locally, you can omit this and use the default SSE server: "
            f"{DEFAULT_PROXY_URL}"
        ),
    )
    parser.add_argument(
        "--sse", action="store_true", help="Run in SSE standalone mode instead of stdio"
    )
    parser.add_argument(
        "--list_tools",
        action="store_true",
        help="List tools that will be available",
    )
    parser.add_argument(
        "--tool_help",
        action="store_true",
        help="Show full help for each tool",
    )

    return parser


def show_tool_info(full_help: bool):
    from kash.exec.action_registry import get_all_actions_defaults
    from kash.help.help_printing import print_action_help
    from kash.mcp.mcp_server_routes import get_published_mcp_tools, publish_mcp_tools
    from kash.shell.output.shell_output import cprint

    publish_mcp_tools()
    tools = get_published_mcp_tools()
    cprint("Actions available as MCP tools:")
    cprint()
    actions = get_all_actions_defaults()
    for tool in tools:
        action = actions[tool]
        print_action_help(
            action, verbose=False, include_options=full_help, include_precondition=full_help
        )
        cprint()


def run_server(args: argparse.Namespace):
    from kash.mcp.mcp_main import McpMode, run_mcp_server
    from kash.workspaces.workspaces import Workspace, get_ws

    log.warning("kash MCP CLI started, logging to: %s", MCP_CLI_LOG_PATH)
    log.warning("Current working directory: %s", Path(".").resolve())

    # Eagerly import so the server is warmed up.
    # This is important to save init time on fresh sandboxes like E2B!
    warm_slow_imports(include_extras=True)

    if args.workspace and args.workspace != global_settings().global_ws_dir:
        with atomic_global_settings().updates() as settings:
            settings.global_ws_dir = Path(args.workspace).absolute()

    ws: Workspace = get_ws(name_or_path=Path(args.workspace), auto_init=True)
    os.chdir(ws.base_dir)
    log.warning("Running in workspace: %s", ws.base_dir)

    mcp_mode = (
        McpMode.standalone_sse
        if args.sse
        else McpMode.proxy_stdio
        if args.proxy
        else McpMode.standalone_stdio
    )
    proxy_to = args.proxy_url or DEFAULT_PROXY_URL if mcp_mode == McpMode.proxy_stdio else None
    run_mcp_server(mcp_mode, proxy_to=proxy_to)


def main():
    args = build_parser().parse_args()

    if args.list_tools or args.tool_help:
        kash_setup(rich_logging=True, log_level=LogLevel.warning)
        show_tool_info(args.tool_help)
    else:
        kash_setup(rich_logging=False, log_level=LogLevel.info)
        run_server(args)


if __name__ == "__main__":
    main()
