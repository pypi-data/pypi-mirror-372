import logging

from fastmcp.server.server import FastMCP

from ..api.app_management import AppManagementAPI
from ..errors.exception import McpToolError
from ..utils.tools_response_format import MCPResponseFormat

mcp_response = MCPResponseFormat()
app = AppManagementAPI()

logger = logging.getLogger(__name__)


def app_management(mcp_instance: FastMCP) -> None:
    """Register the App management tools to manage pCloudy Application functionality"""

    @mcp_instance.tool(
        name="get_all_application",
        description="Get list of all the application",
    )
    async def get_all_application() -> dict:
        try:

            data = await app.filter_ipa_apk()
            return mcp_response.format("json", data, False)

        except Exception as e:
            raise McpToolError("get_all_application", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while fetching Applications: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="upload_app",
        description="This will upload the application to the user account",
    )
    async def upload_app(file_path: str) -> dict:
        try:
            if not file_path:
                return mcp_response.format(
                    "text", "❌ Please provide a file path to upload the app", True
                )

            upload_app_response = await app.upload_app(file_path)
            if "error" in upload_app_response:
                return mcp_response.format(
                    "text",
                    f"❌ Error while uploading the Application: {upload_app_response['error']}",
                    True,
                )

            return mcp_response.format(
                "text",
                f"✅ Application uploaded successfully. Uploaded Application name: {upload_app_response['result']['file']}",
                False,
            )

        except Exception as e:
            raise McpToolError("upload_app", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Error while uploading the Application: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="install_app",
        description="This will install the app on the devices",
    )
    async def install_app(app_name: str, rid: int) -> dict:

        logger.info(f"install_app called with app_name: {app_name}, rid: {rid}")
        try:
            if not rid:
                return mcp_response.format(
                    "text",
                    "❌ rid not available. Please book a device to proceed.",
                    True,
                )

            if not app_name:
                return mcp_response.format(
                    "text", "❌ Please provide the app_name install", True
                )

            install_app_response = await app.install_launch_app(rid, app_name)

            if "error" in install_app_response:
                return mcp_response.format(
                    "text",
                    f"❌ Error while installing the Application: {install_app_response['error']}",
                    True,
                )

            return mcp_response.format(
                "text",
                "✅ Application installed successfully",
                False,
            )

        except Exception as e:
            raise McpToolError("install_app", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while installing the Application: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="resign_app",
        description="This will re-sign the app to make it available for installation on iOS devices",
    )
    async def resign_app(file_name: str) -> dict:
        try:
            # file_name = user_input.strip()

            if not file_name:
                return mcp_response.format(
                    "text",
                    "❌ Please provide the app_name or app to resign",
                    True,
                )

            resign_app_response = await app.perform_ios_resign(file_name)

            if "error" in resign_app_response:
                return mcp_response.format(
                    "text",
                    f"❌ Error while re-signing the Application: {resign_app_response['error']}",
                    True,
                )

            return mcp_response.format(
                "text",
                f"✅ Application re-signed successfully. Resigned app: {resign_app_response['resign_file']}",
                False,
            )

        except Exception as e:
            raise McpToolError("resign_app", {str(e)}) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while re-signing the Application: {str(e)}",
                True,
            )
