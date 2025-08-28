class MCPResponseFormat:
    """
    Utility class to format the response for MCP.
    """

    @staticmethod
    def format(type: str, text: str, is_error: bool) -> dict:
        return {
            "content": [
                {
                    "type": type,
                    "text": text,
                }
            ],
            "isError": is_error,
        }

    @staticmethod
    def device_detail_format(device: dict) -> str:
        """
        Format the response for device details as JSON string.
        """
        details = [
            f"🔹 Device ID: {device['device_id']}",
            f"🔹 Display Name: {device['display_name']}",
            f"🔹 Model: {device['model']}",
            f"🔹 Manufacturer: {device['manufacturer']}",
            f"🔹 Platform: {device['platform']}",
            f"🔹 OS Version: {device['version']}",
            f"🔹 Available: {'✅ Yes' if device['available'] else '❌ No'}",
            f"🔹 RAM: {device['ram'] // 1024}GB",
            f"🔹 Resolution: {device['resolution']}",
            f"🔹 Display Size: {device['display_area']} inches",
            f"🔹 CPU: {device['cpu']}",
            f"🔹 DPI: {device['dpi']}",
            f"🔹 Alias: {device['alias_name']}",
        ]

        return MCPResponseFormat.format("text", "\n".join(details), is_error=False)

    @staticmethod
    def qpilot_no_app_details_reponse(platform: str) -> str:
        if platform.lower() == "android":
            response = (
                "📱 **Android App Details Required:**\n\n"
                + "Please provide the following details:\n\n"
                + "```\n"
                + "App Name: YourAppName\n"
                + "App Package: com.example.yourapp\n"
                + "App Activity: com.example.yourapp.MainActivity\n"
                + "```\n\n"
                + "**Optional - Specify QPilot Project Details:**\n"
                + "```\n"
                + "Project: YourProjectName\n"
                + "Suite: YourTestSuite\n"
                + "TestCase: YourTestCase\n"
                + "```\n\n"
                + "**Example with steps:**\n"
                + "App Name: Instagram\n"
                + "App Package: com.instagram.android\n"
                + "App Activity: com.instagram.android.activity.MainTabActivity\n"
                + "Project: My Test Project\n"
                + "Suite: Login Tests\n"
                + "TestCase: Valid Login Test\n\n"
                + "Enter username 'test@gmail.com'\n"
                + "Enter password 'password'\n"
                + "Click login button\n\n"
                + "**Note:** If you don't specify project/suite/testcase, default values will be used."
            )
        else:
            response = (
                "📱 **iOS App Details Required:**\n\n"
                + "Please provide the following details:\n\n"
                + "```\n"
                + "App Name: YourAppName\n"
                + "Bundle ID: com.example.yourapp\n"
                + "```\n\n"
                + "**Optional - Specify QPilot Project Details:**\n"
                + "```\n"
                + "Project: YourProjectName\n"
                + "Suite: YourTestSuite\n"
                + "TestCase: YourTestCase\n"
                + "```\n\n"
                + "**Example with steps:**\n"
                + "App Name: Instagram\n"
                + "Bundle ID: com.burbn.instagram\n"
                + "Project: My Test Project\n"
                + "Suite: Login Tests\n"
                + "TestCase: Valid Login Test\n\n"
                + "Enter username 'test@gmail.com'\n"
                + "Enter password 'password'\n"
                + "Click login button\n\n"
                + "**Note:** If you don't specify project/suite/testcase, default values will be used."
            )
        return response

    @staticmethod
    def qpilot_no_steps_error_reponse(
        app_name: str, app_package: str, app_activity: str, platform: str
    ) -> str:
        response = (
            f"✅ **App Details Configured:**\n"
            f"• App Name: {app_name}\n"
            f"• {'Bundle ID' if platform.lower() == 'ios' else 'App Package'}: {app_package}\n"
            + (
                f"• App Activity: {app_activity}\n"
                if platform.lower() == "android"
                else ""
            )
            + "\n📝 **Now enter the steps to execute:**\n\n"
            + "⚠️ **IMPORTANT FORMAT REQUIREMENT:**\n"
            + "Each step should be on a NEW LINE. Example:\n\n"
            + "Enter username 'user@gmail.com'\n"
            + "Enter password 'password'\n"
            + "Click login button\n"
            + "Verify dashboard appears"
        )
        return response

    @staticmethod
    def qpilot_no_steps_error_reponse_browser() -> str:
        response = (
            "⚠️ **IMPORTANT FORMAT REQUIREMENT:**\n"
            "Each step should be on a NEW LINE. Example:\n\n"
            "Enter username 'user@gmail.com'\n"
            "Enter password 'password'\n"
            "Click login button\n"
            "Verify dashboard appears"
        )
        return response

    @staticmethod
    def qpilot_missing_app_details_response(platform: str, missing_fields: list) -> str:
        if platform.lower() == "android":
            response = (
                f"❌ Missing required Android app details: {', '.join(missing_fields)}\n\n"
                + "Please provide all fields:\n"
                + "App Name: YourAppName\n"
                + "App Package: com.example.yourapp\n"
                + "App Activity: com.example.yourapp.MainActivity"
            )
        else:
            response = (
                f"❌ Missing required iOS app details: {', '.join(missing_fields)}\n\n"
                + "Please provide all fields:\n"
                + "App Name: YourAppName\n"
                + "Bundle ID: com.example.yourapp"
            )
        return response
