"""Main entry point with FastMCP error handling."""

import logging
import sys

from .errors.exception import AppStartupError
from .logger.logger import setup_logging
from .server import create_server
from .utils.config import Config


def main() -> None:
    """Main entry point with comprehensive error handling."""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.debug("__main__ called")

        config = Config()
        if not config:
            raise AppStartupError("config", "Failed to load configuration")

        logger.info("Starting FastMCP application...")

        server = create_server(config)
        server.run()

    except AppStartupError as e:
        logger.error(f"{e}")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
