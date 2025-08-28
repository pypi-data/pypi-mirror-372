import logging

from fastmcp.server.server import FastMCP

from ..api.browser_booking import BrowserBooking
from ..errors.exception import McpToolError
from ..utils.tools_response_format import MCPResponseFormat

mcp_response = MCPResponseFormat()
browser_booking = BrowserBooking()
logger = logging.getLogger(__name__)


def browser_booking_management(mcp_instance: FastMCP) -> None:
    """Register Browser management tools with FastMCP instance."""

    @mcp_instance.tool(
        name="get_browser_list",
        description="Get list of available browser from pCloudy for specified machines",
    )
    async def get_browser_list() -> dict:
        try:
            available_browsers = await browser_booking.get_browser_list()
            if not available_browsers:
                return mcp_response.format(
                    "text",
                    f"No machines available.",
                    True,
                )
            return mcp_response.format(
                "text",
                f"Available browsers {available_browsers}",
                False,
            )

        except Exception as e:
            raise McpToolError("get_browser_list", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error getting browser list: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="book_browser",
        description="Book a browser on a specified VM",
    )
    async def book_browser(vm_id: str, browser: str, browserVersion: str) -> dict:
        try:
            booking_response = await browser_booking.book_browser(
                vm_id, browser, browserVersion
            )
            if not booking_response:
                return mcp_response.format(
                    "text",
                    f"Failed to book browser.",
                    True,
                )
            return mcp_response.format(
                "text",
                f"Successfully booked browser {booking_response}.",
                False,
            )
        except Exception as e:
            raise McpToolError("book_browser", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error booking browser: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="get_browser_live_view_url",
        description="Get the live view URL for a booked browser session",
    )
    async def get_browser_live_view_url(
        vm_id: str, os: str, osVer: str, browser: str, browserVersion: str
    ) -> dict:
        try:
            live_view_url = await browser_booking.view_live_url(
                vm_id, os, osVer, browser, browserVersion
            )
            if not live_view_url:
                return mcp_response.format(
                    "text",
                    f"Failed to get live view URL.",
                    True,
                )
            return mcp_response.format(
                "text",
                f"Successfully retrieved live view URL: {live_view_url}.",
                False,
            )

        except Exception as e:
            raise McpToolError("get_browser_live_view_url", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error getting live view URL: {str(e)}",
                True,
            )

    async def get_browser_list() -> dict:
        try:
            available_browsers = await browser_booking.get_browser_list()
            if not available_browsers:
                return mcp_response.format(
                    "text",
                    f"No machines available.",
                    True,
                )
            return mcp_response.format(
                "text",
                f"Available browsers {available_browsers}",
                False,
            )

        except Exception as e:
            raise McpToolError("get_browser_list", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error getting browser list: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="release_browser",
        description="Release a booked browser on a specified VM",
    )
    async def release_browser(vm_id: str, booking_id: str) -> dict:
        try:
            release_response = await browser_booking.release_vm(vm_id, booking_id)
            if not release_response:
                return mcp_response.format(
                    "text",
                    f"Failed to release browser.",
                    True,
                )
            return mcp_response.format(
                "text",
                f"Successfully released browser {release_response}.",
                False,
            )

        except Exception as e:
            raise McpToolError("release_browser", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error releasing browser: {str(e)}",
                True,
            )
