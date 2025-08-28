import json
import logging

from ..Constant.constant import Constant
from ..utils.config import Config
from .authenticate import AuthAPI
from .http_client import HttpClient

logger = logging.getLogger(__name__)
constant = Constant()
config = Config()
origin = constant.qpilot.get_qpilot_origin()
cloud_url = config.userdetail.pcloudy_cloud_url


class QPilot(HttpClient):
    """
    This class handles QPilot operations in the pCloudy MCP application.
    It provides methods for different QPilot actions.
    """

    async def get_credit_balance(self) -> dict:

        auth_api = AuthAPI()
        token = await auth_api.get_token()

        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }
        response = await self.get(
            constant.pclodyApiEndpoint.GET_CREDIT_BALANCE,
            headers=headers,
        )

        return response

    async def get_project_list(self) -> dict:

        auth_api = AuthAPI()

        token = await auth_api.get_token()

        payload = {"getShared": True}
        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.GET_PROJECT_LIST,
            data=payload,
            headers=headers,
        )
        return response

    async def create_project(self, project_name: str) -> dict:

        auth_api = AuthAPI()
        token = await auth_api.get_token()

        payload = {"name": project_name}
        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.CREATE_PROJECT,
            data=payload,
            headers=headers,
        )
        return response

    async def get_testsuite_list(self) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.GET_TESTSUITE_LIST,
            headers=headers,
        )
        return response

    async def create_testsuite(self, testsuite_name: str) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        payload = {"testSuiteName": testsuite_name}
        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.CREATE_TESTSUITE,
            data=payload,
            headers=headers,
        )
        return response

    async def get_testcase_list(self) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        payload = {"getShared": True}
        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.GET_TESTCASE_LIST,
            data=payload,
            headers=headers,
        )
        return response

    async def create_testcase(
        self,
        testsuite_id: str,
        testcase_name: str,
        platform: str,
    ) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        payload = {
            "testSuiteId": testsuite_id,
            "testCaseName": testcase_name,
            "platform": platform,
        }

        headers = {
            "Content-Type": "application/json",
            "token": token,
            "Origin": origin,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.CREATE_TESTCASE,
            data=payload,
            headers=headers,
        )
        return response

    async def start_wda_ios(self, rid: int) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        payload = {"rid": rid, "action": "start", "os": "ios"}
        headers = {
            "Content-Type": "application/json",
            "token": token,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.START_WDA_IOS,
            data=payload,
            headers=headers,
        )
        return response

    async def start_appium(self, rid: int, app_name: str, platform: str) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        payload = {
            "rid": rid,
            "action": "start",
            "os": platform,
            "appName": app_name,
        }

        headers = {
            "Content-Type": "application/json",
            "token": token,
        }

        response = await self.post(
            constant.pclodyApiEndpoint.START_APPIUM,
            data=payload,
            headers=headers,
        )
        return response

    async def generate_code(
        self,
        rid: int,
        app_name: str,
        description: str,
        test_id: str,
        suite_id: str,
        app_package: str,
        app_activity: str,
        steps: str,
        project_id: str,
        platform: str,
    ) -> dict:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        if app_name and not app_name.lower().endswith((".apk", ".ipa")):
            return {
                "error": f"Invalid app '{app_name}'. Only .apk or .ipa files are allowed."
            }

        app_activity = app_activity or ""

        if platform.lower() == "ios":
            wda_response = await self.start_wda_ios(rid)
            if wda_response.get("error"):
                return {"error": f"WDA start failed: {wda_response['error']}"}
            appium_response = await self.start_appium(rid, app_name, "ios")
            if appium_response.get("error"):
                return {"error": f"Appium start failed: {appium_response['error']}"}

        elif platform.lower() == "android":
            appium_response = await self.start_appium(rid, app_name, "android")
            if appium_response.get("error"):
                return {"error": f"Appium start failed: {appium_response['error']}"}

        else:
            return {"error": f"Unsupported platform: {platform}"}

        payload = {
            "rid": rid,
            "description": description,
            "testId": test_id,
            "suiteId": suite_id,
            "appPackage": app_package,
            "appName": app_name,
            "appActivity": app_activity,
            "steps": steps.strip(),
            "projectId": project_id,
            "testdata": {},
        }

        headers = {
            "Content-Type": "application/json",
            "Cookie": f"PYPCLOUDY={token}",
        }
        response = await self.post(
            constant.pclodyApiEndpoint.GENERATE_CODE,
            data=payload,
            headers=headers,
        )
        return response

    async def get_playwright_ws_endpoint(
        self, vm_id: str, browser: str, browser_version: str
    ) -> str:
        auth_api = AuthAPI()
        token = await auth_api.get_token()

        headers = {
            "Content-Type": "application/json",
            "Origin": cloud_url,
            "token": token,
        }

        payload = {"browser": browser, "version": browser_version}

        response = await self.post(
            constant.pclodyApiEndpoint.BOOK_VM + f"/{vm_id}/playwright-endpoint",
            headers=headers,
            data=payload,
        )

        return response.get("playwrightEndpoint", "")

    async def generate_code_browser(
        self,
        feature_name: str,
        test_id: str,
        suite_id: str,
        steps: str,
        vm_id: str,
        browser: str,
        browser_version: str,
        url: str,
    ) -> dict:

        auth_api = AuthAPI()
        token = await auth_api.get_token()

        cloud_url = config.userdetail.pcloudy_cloud_url

        payload = {
            "testCaseId": test_id,
            "testSuiteId": suite_id,
            "config": {
                "featureName": feature_name,
                "metadata": {"url": url},
                "steps": steps.strip(),
            },
            "platform": "web",
            "vmAutomationUrl": await self.get_playwright_ws_endpoint(
                vm_id, browser, browser_version
            ),
            "testdata": {},
        }

        headers = {
            "Content-Type": "application/json",
            "Origin": cloud_url,
            "token": token,
        }
        response = await self.post(
            constant.pclodyApiEndpoint.GENERATE_CODE_BROWSER,
            data=payload,
            headers=headers,
        )

        return response
