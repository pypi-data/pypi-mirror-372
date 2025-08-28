"""Config-based tool registration for FastMCP server."""

import importlib
import logging

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_tools_with_config(mcp_instance: FastMCP) -> None:
    """Register tools using the utils/tools_config.py file.

    Args:
        mcp_instance: The FastMCP instance to register tools with
    """
    try:
        # Import the config module from same directory (utils/)
        from .tools_config import ENABLED_TOOLS

        if not ENABLED_TOOLS:
            logger.warning("No tools enabled in ENABLED_TOOLS")
            return

        registered_count = 0
        failed_count = 0

        for module_name, function_name in ENABLED_TOOLS:
            try:
                # Import the tool module from tools directory
                # Go up one level (..tools) to access tools folder
                module = importlib.import_module(
                    f"..tools.{module_name}", package=__package__
                )

                # Get the registration function
                register_func = getattr(module, function_name)

                # Call the registration function
                register_func(mcp_instance)

                registered_count += 1
                logger.info(f"✓ Registered {module_name}")

            except ImportError as e:
                logger.warning(f"⚠ Module {module_name} not found: {e}", exc_info=True)
                failed_count += 1

            except AttributeError as e:
                logger.error(
                    f"✗ Function {function_name} not found in {module_name}: {e}",
                    exc_info=True,  # ✅ include stack trace
                )
                failed_count += 1

            except Exception as e:
                logger.exception(f"✗ Failed to register {module_name}: {e}")
                failed_count += 1

        # Summary
        total_tools = len(ENABLED_TOOLS)
        logger.info(
            f"Registration complete: {registered_count}/{total_tools} tools registered"
        )

        if failed_count > 0:
            logger.warning(f"{failed_count} tools failed to register")

    except ImportError:
        logger.error("tools_config.py not found in utils directory")
        raise
    except Exception as e:
        logger.error(f"Failed to load tools config: {e}")
        raise
