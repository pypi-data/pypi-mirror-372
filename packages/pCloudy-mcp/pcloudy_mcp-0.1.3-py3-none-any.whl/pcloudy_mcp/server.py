"""FastMCP Server implementation with config-based tool registration."""

import asyncio
import logging
import signal

from fastmcp import FastMCP

from .Constant.constant import Constant
from .errors.exception import ServerInitializationError
from .utils.config import Config

logger = logging.getLogger(__name__)


class MCPServer:
    """Custom FastMCP Server with robust error handling."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._shutdown_event = asyncio.Event()
        self.mcp = FastMCP(
            name=Constant.mcpServer.SERVER_NAME,
            version=Constant.mcpServer.SERVER_VERSION,
        )
        self._setup_server()

    def _setup_server(self) -> None:
        try:
            self._setup_signal_handlers()
            self._register_tools()
            logger.info(
                f"FastMCP server '{Constant.mcpServer.SERVER_NAME}' initialized successfully"
            )
        except Exception as e:
            raise ServerInitializationError("Server Setup", str(e)) from e

    def _register_tools(self) -> None:
        try:
            from .utils.tools_auto_registry import register_tools_with_config

            register_tools_with_config(self.mcp)
            logger.info("All tools from config registered successfully")
        except ImportError as e:
            raise ServerInitializationError(
                "Tool Registration", f"ImportError: {e}"
            ) from e
        except Exception as e:
            raise ServerInitializationError("Tool Registration", str(e)) from e

    def _setup_signal_handlers(self) -> None:
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_event.set()

        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            logger.warning("Could not set signal handlers - not in main thread")

    def run(self) -> None:
        try:
            logger.info(
                f"Starting FastMCP server '{Constant.mcpServer.SERVER_NAME}' v{Constant.mcpServer.SERVER_VERSION}"
            )
            self.mcp.run()
        except KeyboardInterrupt:
            logger.info("Server stopped by user (Ctrl+C)")
        except ConnectionError as e:
            raise ServerInitializationError(
                "Server Run", f"Connection error: {e}"
            ) from e
        except Exception as e:
            logger.exception("Full traceback:")
            raise ServerInitializationError("Server Run", str(e)) from e
        finally:
            logger.info("Server shutdown complete")
            self._shutdown_event.set()

    async def run_async(self) -> None:
        try:
            logger.info(
                f"Starting FastMCP server '{Constant.mcpServer.SERVER_NAME}' v{Constant.mcpServer.SERVER_VERSION}"
            )
            await self.mcp.run_async()
        except KeyboardInterrupt:
            logger.info("Server stopped by user (Ctrl+C)")
        except ConnectionError as e:
            raise ServerInitializationError(
                "Server Run (Async)", f"Connection error: {e}"
            ) from e
        except asyncio.CancelledError:
            logger.info("Server operation was cancelled")
            raise
        except Exception as e:
            logger.exception("Full traceback:")
            raise ServerInitializationError("Server Run (Async)", str(e)) from e
        finally:
            logger.info("Server shutdown complete")
            self._shutdown_event.set()

    async def shutdown(self) -> None:
        logger.info("Initiating graceful shutdown...")
        self._shutdown_event.set()

    def get_mcp_instance(self) -> FastMCP:
        return self.mcp


def create_server(config: Config) -> MCPServer:
    if not config:
        raise ServerInitializationError("Config Validation", "Invalid configuration")

    server = MCPServer(config)
    logger.info("FastMCP server created successfully")
    return server


def run_server(config: Config) -> None:
    try:
        server = create_server(config)
        server.run()
    except Exception as e:
        raise ServerInitializationError("Run Server", str(e)) from e


async def run_server_async(config: Config) -> None:
    try:
        server = create_server(config)
        await server.run_async()
    except Exception as e:
        raise ServerInitializationError("Run Server Async", str(e)) from e
