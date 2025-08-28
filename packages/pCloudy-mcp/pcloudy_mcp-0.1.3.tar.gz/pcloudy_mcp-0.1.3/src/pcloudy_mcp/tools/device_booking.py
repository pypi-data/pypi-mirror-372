import logging

from fastmcp.server.server import FastMCP

from ..api.device_booking import DeviceBooking
from ..errors.exception import McpToolError
from ..utils.token_cache import delete_cached_token
from ..utils.tools_response_format import MCPResponseFormat

mcp_response = MCPResponseFormat()

logger = logging.getLogger(__name__)


def device_booking_management(mcp_instance: FastMCP) -> None:
    """Register device management tools with FastMCP instance."""

    @mcp_instance.tool(
        name="get_device_list",
        description="Get list of available devices from pCloudy for specified platform",
    )
    async def get_device_list(platform: str) -> dict:
        try:

            platform_lower = platform.lower()
            if platform_lower not in ["android", "ios"]:
                return mcp_response.format(
                    "text",
                    f"Unsupported platform: {platform}. Use 'android' or 'ios'",
                    True,
                )

            device_booking = DeviceBooking()
            device_list = await device_booking.get_device_list(platform=platform_lower)

            if device_list.get("result", {}).get("code") != 200:
                return mcp_response.format(
                    "text",
                    "❌ Failed to fetch device list. API error.",
                    True,
                )

            devices = device_list.get("result", {}).get("models", [])
            available = [d for d in devices if d.get("available", False)]

            if not available:
                return mcp_response.format(
                    "text",
                    f"No {platform_lower} devices available.",
                    True,
                )

            device_info = []
            for device in available:
                device_id = device.get("id", "Unknown")
                display_name = device.get("display_name", "Unknown")
                model = device.get("model", "Unknown")
                version = device.get("version", "Unknown")
                full_name = device.get("full_name", "Unknown")
                ram = device.get("ram", 0)
                ram_gb = f"{ram // 1024}GB" if ram > 0 else "Unknown"
                resolution = device.get("resolution", "Unknown")

                device_info.append(
                    f"ID: {device_id} | {display_name} ({model}) | Android {version} | {ram_gb} RAM | {resolution} | Full name : {full_name}"
                )
            return mcp_response.format(
                "text",
                f"Available {platform_lower} devices:\n\n" + "\n".join(device_info),
                False,
            )

        except Exception as e:
            raise McpToolError("get_device_list", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error getting device list: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="book_device",
        description="Book a device from pCloudy using device name (e.g., 'realme GT Neo2')",
    )
    async def book_device(device_name: str, platform: str = "android") -> dict:
        try:
            if not device_name or not device_name.strip():
                return mcp_response.format(
                    "text",
                    "Device name is required. Use get_device_list to see available devices.",
                    True,
                )

            platform_lower = platform.lower()
            if platform_lower not in ["android", "ios"]:
                return mcp_response.format(
                    "text",
                    f"Unsupported platform: {platform}. Use 'android' or 'ios'",
                    True,
                )

            device_booking = DeviceBooking()
            device_list = await device_booking.get_device_list(platform=platform_lower)

            if device_list.get("result", {}).get("code") != 200:
                logger.error(device_list)
                return mcp_response.format(
                    "text",
                    "❌ Failed to fetch device list. API error.",
                    True,
                )

            devices = device_list.get("result", {}).get("models", [])
            available_devices = [d for d in devices if d.get("available", False)]

            search_name = device_name.strip().lower()
            target_device = next(
                (
                    device
                    for device in available_devices
                    if search_name in device.get("display_name", "").lower()
                    or search_name in device.get("model", "").lower()
                ),
                None,
            )

            if not target_device:
                available_names = [
                    d.get("display_name", "Unknown") for d in available_devices[:5]
                ]
                return mcp_response.format(
                    "text",
                    f"❌ Device '{device_name}' not found or not available.\n\n"
                    f"Available devices: {', '.join(available_names)}",
                    True,
                )

            device_id = target_device.get("id")
            booking_result = await device_booking.book_device(
                platform=platform_lower, device_id=device_id
            )

            result = booking_result.get("result", {})
            if result.get("code") == 200:
                rid = result.get("rid", "Unknown")
                device_display_name = target_device.get("display_name", "Unknown")
                return mcp_response.format(
                    "text",
                    f"✅ Device booked successfully!\n"
                    f"Device: {device_display_name}\n"
                    f"Device ID: {device_id}\n"
                    f"RID : {int(rid)}",
                    False,
                )
            else:
                error_code = result.get("code", "Unknown")
                logger.error(
                    f"Failed to book device {device_id}: API returned code {error_code}"
                )
                return mcp_response.format(
                    "text",
                    f"❌ Failed to book device: API returned error code {error_code}",
                    True,
                )

        except Exception as e:
            raise McpToolError("book_device", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error booking device: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="get_device_details",
        description="Get detailed information about a specific device by ID",
    )
    async def get_device_details(device_id: str, platform: str) -> dict:
        try:
            if not device_id or not device_id.strip():
                return mcp_response.format(
                    "text",
                    "Device ID is required. Use get_device_list to see available devices.",
                    True,
                )

            platform_lower = platform.lower()
            if platform_lower not in ["android", "ios"]:
                return mcp_response.format(
                    "text",
                    f"Unsupported platform: {platform}. Use 'android' or 'ios'",
                    True,
                )

            device_booking = DeviceBooking()
            device_list = await device_booking.get_device_list(platform=platform_lower)

            devices = device_list.get("result", {}).get("models", [])
            target_device = next(
                (d for d in devices if str(d.get("id")) == device_id.strip()), None
            )

            if not target_device:
                return mcp_response.format(
                    "text",
                    f"❌ Device with ID {device_id} not found. "
                    "Use get_device_list to see available devices.",
                    True,
                )

            device_data = {
                "device_id": target_device.get("id", "Unknown"),
                "display_name": target_device.get("display_name", "Unknown"),
                "model": target_device.get("model", "Unknown"),
                "manufacturer": target_device.get("manufacturer", "Unknown"),
                "platform": target_device.get("platform", "Unknown").upper(),
                "version": target_device.get("version", "Unknown"),
                "available": target_device.get("available", False),
                "ram": target_device.get("ram", 0),
                "resolution": target_device.get("resolution", "Unknown"),
                "display_area": target_device.get("display_area", "Unknown"),
                "cpu": target_device.get("cpu", "Unknown"),
                "dpi": target_device.get("dpi", "Unknown"),
                "alias_name": target_device.get("alias_name", "Unknown"),
                "full_name": target_device.get("full_name", "Unknown"),
            }

            return mcp_response.device_detail_format(device_data)

        except Exception as e:
            raise McpToolError("get_device_details", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error getting device details: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="get_live_view_url",
        description="Get live view URL for a booked device",
    )
    async def get_live_view_url(rid: int) -> dict:
        try:
            if not rid or rid <= 0:
                return mcp_response.format(
                    "text",
                    "Valid booking ID (RID) is required.",
                    True,
                )

            device_booking = DeviceBooking()
            live_view_result = await device_booking.get_live_view_url(rid=rid)

            result = live_view_result.get("result", {})
            if result.get("code") == 200:
                url = result.get("URL", "")
                if url:
                    return mcp_response.format(
                        "text",
                        f"✅ Live view URL:\n{url}",
                        False,
                    )

                logger.error(f"Empty URL received for RID {rid}")
                return mcp_response.format(
                    "text",
                    "❌ Empty URL received from API. Please try again later.",
                    True,
                )

            error_code = result.get("code", "Unknown")
            logger.error(
                f"Failed to get live view URL for RID {rid}: API returned code {error_code}"
            )
            return mcp_response.format(
                "text",
                f"❌ Failed to get live view URL: error code {error_code}",
                True,
            )
        except Exception as e:
            raise McpToolError("get_live_view_url", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error getting live view URL: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="release_device",
        description="Release a booked device using booking ID (RID)",
    )
    async def release_device(rid: int) -> dict:
        try:
            if not rid or rid <= 0:
                return mcp_response.format(
                    "text",
                    "Valid booking ID (RID) is required.",
                    True,
                )

            device_booking = DeviceBooking()
            release_result = await device_booking.release_device(rid=rid)

            result = release_result.get("result", {})

            if result.get("code") == 200:
                message = result.get("msg", "Device released successfully")
                return mcp_response.format(
                    "text",
                    f"✅ Device released:\n{message}",
                    False,
                )

            error_code = result.get("code", "Unknown")
            error_msg = result.get("msg", "Unknown error")

            return mcp_response.format(
                "text",
                f"❌ Failed to release device: {error_code}\nMessage: {error_msg}",
                True,
            )
        except Exception as e:
            raise McpToolError("release_device", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Exception releasing device: {release_device(e)}",
                True,
            )

    @mcp_instance.tool(
        name="refresh_authentication",
        description="It refresh the user authentication",
    )
    async def refresh_authentication() -> dict:
        try:
            refresh = delete_cached_token()
            if not refresh.get("success"):
                return mcp_response.format("text", f"{refresh.get('message')}", True)
            return mcp_response.format("text", f"{refresh.get('message')}", False)
        except Exception as e:
            raise McpToolError("refresh_authentication", {str(e)}) from e
            return mcp_response.format("text", "❌ Error While re-fresh", True)
