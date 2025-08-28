import asyncio
import logging
from pathlib import Path

from ..Constant.constant import Constant
from ..utils.config import Config
from .authenticate import AuthAPI
from .http_client import HttpClient

logger = logging.getLogger(__name__)
constant = Constant()
config = Config()
auth_api = AuthAPI()


class AppManagementAPI(HttpClient):
    """
    This class provides methods to manage applications on the pCloudy platform.
    It includes functionalities to upload, delete, resign, and list applications.
    """

    async def upload_app(self, file_path: str, filter_value: str = "all") -> dict:
        token = await auth_api.get_token()

        # Convert to Path object (cross-platform safe)
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return {"error": f"Path does not exist: '{file_path}'"}

        # Proceed with file upload
        with open(file_path_obj, "rb") as file_handle:
            files = {
                "file": (file_path_obj.name, file_handle),
                "source_type": (None, "raw"),
                "token": (None, token),
                "filter": (None, filter_value),
            }

            response = await self.post(
                constant.pclodyApiEndpoint.UPLOAD_APP,
                data=None,
                headers=None,
                files=files,
            )

        return response

    async def list_app(self, limit: str = "all", filter: str = "all") -> dict:
        token = await auth_api.get_token()
        payload = {"token": token, "limit": limit, "filter": filter}

        headers = {
            "Content-Type": "application/json",
        }
        response = await self.post(
            constant.pclodyApiEndpoint.AVALIABLE_APPS,
            data=payload,
            headers=headers,
        )
        return response

    async def install_launch_app(self, rid: int, filename: str) -> dict:
        if not (filename.lower().endswith(".apk") or filename.lower().endswith(".ipa")):
            return {
                "error": f"Invalid file type: '{filename}'. Only .apk or .ipa files are allowed."
            }
        app_list_response = await self.filter_ipa_apk()
        if app_list_response["status"] == "success":
            data = app_list_response["data"]
            if filename.lower().endswith(".ipa"):
                if filename not in data.get("ipa", []):
                    return {
                        "error": f"'{filename}' not available in app list. Please upload it first."
                    }
            elif filename.lower().endswith(".apk"):
                if filename not in data.get("apk", []):
                    return {
                        "error": f"'{filename}' not available in app list. Please upload it first."
                    }

        token = await auth_api.get_token()
        payload = {
            "token": token,
            "rid": rid,
            "filename": filename,
            "grant_all_permissions": "true",
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = await self.post(
            constant.pclodyApiEndpoint.INSTALL_AND_LAUNCH_APP,
            data=payload,
            headers=headers,
        )
        if not response.get("result", {}).get("code") == 200:
            return {"error": response}
        return response

    async def perform_ios_resign(self, filename: str) -> dict:
        if not (filename.lower().endswith(".apk") or filename.lower().endswith(".ipa")):
            return {
                "error": f"Invalid file type: '{filename}'. Only .apk or .ipa files are allowed."
            }
        app_list_response = await self.filter_ipa_apk()

        if app_list_response["status"] == "success":
            data = app_list_response["data"]
            if filename.lower().endswith(".ipa"):
                if filename not in data.get("ipa", []):
                    return {
                        "error": f"'{filename}' not available in app list. Please upload it first."
                    }
            elif filename.lower().endswith(".apk"):
                if filename not in data.get("apk", []):
                    return {
                        "error": f"'{filename}' not available in app list. Please upload it first."
                    }
        token = await auth_api.get_token()
        # Step 1: Resign Initiate
        initiate_payload = {
            "token": token,
            "filename": filename,
        }

        initiate_response = await self.post(
            constant.pclodyApiEndpoint.INITIATE_IOS_RESIGN,
            data=initiate_payload,
            headers={"Content-Type": "application/json"},
        )

        result = initiate_response.get("result", {})
        resign_token = result.get("resign_token")
        resign_filename = result.get("resign_filename")

        if not resign_token or not resign_filename:
            return {"error": result}

        # Step 2: Poll Resign Progress
        progress_payload = {
            "token": token,
            "resign_token": resign_token,
            "filename": resign_filename,
        }

        max_retries = constant.MAXIMUM_RETRIES_RESIGN_PROGRESS
        retry_count = 0
        await asyncio.sleep(1)  # brief wait before polling

        while retry_count < max_retries:
            progress_response = await self.post(
                constant.pclodyApiEndpoint.PROGRESS_IOS_RESIGN,
                data=progress_payload,
                headers={"Content-Type": "application/json"},
            )
            resign_status = progress_response.get("result", {}).get("resign_status", 0)

            if resign_status == 100:
                break

            retry_count += 1
            await asyncio.sleep(5)  # wait before next poll

        if resign_status != 100:
            return {"error": "Resign progress polling timed out or failed"}

        # Step 3: Resign Download
        download_payload = {
            "token": token,
            "resign_token": resign_token,
            "filename": resign_filename,
        }

        download_response = await self.post(
            constant.pclodyApiEndpoint.DOWNLOAD_IOS_RESIGN,
            data=download_payload,
            headers={"Content-Type": "application/json"},
        )

        resign_file = download_response.get("result", {}).get("resign_file")

        if not resign_file:
            return {
                "error": "Resign download failed: Missing 'resign_file' in response"
            }

        return {
            "resign_file": resign_file,
            "status": "success",
        }

    async def filter_ipa_apk(self) -> dict:
        app_list_response = await self.list_app()

        if app_list_response.get("result", {}).get("code") == 200:
            file_names = [
                file_entry["file"]
                for file_entry in app_list_response["result"]["files"]
            ]
            apk_files = [file for file in file_names if file.lower().endswith(".apk")]
            ipa_files = [file for file in file_names if file.lower().endswith(".ipa")]
            app_file_dict = {
                "apk": apk_files,
                "ipa": ipa_files,
            }
            return {"status": "success", "data": app_file_dict}
        else:
            logger.error(app_list_response)
            return {"status": "error"}
