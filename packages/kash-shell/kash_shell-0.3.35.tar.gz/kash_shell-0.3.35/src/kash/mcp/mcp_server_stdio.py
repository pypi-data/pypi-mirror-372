import asyncio
import logging
import sys

from anyio import ClosedResourceError
from mcp.server.stdio import stdio_server

from kash.mcp import mcp_server_routes

log = logging.getLogger(__name__)


def run_mcp_server_stdio():
    """
    Runs the MCP server in stdio mode, blocking until completion.
    """

    async def arun():
        log.info("Starting MCP server in stdio mode")
        try:
            async with stdio_server() as (read_stream, write_stream):
                # Uses the same base server as the SSE version
                server = mcp_server_routes.create_base_server()
                await server.run(read_stream, write_stream, server.create_initialization_options())
        except ClosedResourceError as e:
            log.warning("Stream was closed: %s", e)
            # Gracefully exit when the stream is closed
            return
        except Exception as e:
            log.error("Error in MCP server stdio mode: %s", e)
            raise

    try:
        # For stdio mode, we just run until completion.
        asyncio.run(arun())
    except Exception:
        log.exception("MCP Server (stdio) failed with error")
        sys.exit(1)
