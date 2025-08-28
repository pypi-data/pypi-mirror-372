import json
import logging
from urllib.parse import urlparse

from ..Constant.constant import Constant
from ..utils.config import Config
from .authenticate import AuthAPI
from .http_client import HttpClient

logger = logging.getLogger(__name__)
constant = Constant()
auth_api = AuthAPI()
config = Config()

cloud_url = config.userdetail.pcloudy_cloud_url


class BrowserBooking(HttpClient):
    """
    This class handles Browser booking operations in the pCloudy MCP application.
    It provides methods to book Browsers, get Browser list, live view URL, and release bookings.
    """

    async def get_browser_list(self) -> dict:
        """
        Retrieve the list of Browsers available for booking.

        Returns:
            dict: A dictionary containing the list of Browsers or error.
        """
        token = await auth_api.get_token()

        headers = {
            "Content-Type": "application/json",
            "Origin": cloud_url,
            "token": token,
        }
        response = await self.post(
            constant.pclodyApiEndpoint.GET_VMS,
            headers=headers,
        )
        available_vms = [
            {
                "os": item["os"],
                "osVer": item["osVer"],
                "vmId": item["vmId"],
                "browsers": item["browser"],
            }
            for item in response
            if item.get("isBooked") == "false"
        ]
        return available_vms

    async def book_browser(self, vm_id: str, browser: str, browserVersion: str) -> dict:
        """
        Book a browser in a particular VM.

         Args:
            vm_id (str): Id of which VM need to booked.
            browser (str): Name of the browser which need to book.
                        browserVersion (str): Version of the browser whcih need to book

        Returns:
           dict: API response with booking details or error.
        """
        token = await auth_api.get_token()

        headers = {
            "Content-Type": "application/json",
            "Origin": cloud_url,
            "token": token,
        }
        payload = {"browser": browser, "version": browserVersion}
        response = await self.post(
            constant.pclodyApiEndpoint.BOOK_VM + f"/{vm_id}/book",
            headers=headers,
            data=payload,
        )

        # Clean trialUser from the response if present
        if (
            isinstance(response, dict)
            and "result" in response
            and "data" in response["result"]
        ):
            data = response["result"]["data"]

            # remove trialUser only
            data.pop("trialUser", None)

        return response

    async def view_live_url(
        self, vm_id: str, os: str, osVer: str, browser: str, browserVersion: str
    ) -> dict:
        """
        Get the live view URL for a booked browser session
        Args:
                vm_id (str): The ID of the vm booked.
                os (str): The operating system of the vm booked.
                osVer (str): The version of the operating system of the vm booked.
                browser (str): The browser being used.
                browserVersion (str): The version of the browser being used
        Returns:
                dict: A dictionary containing the live view URL or error.
        """
        parsed_url = urlparse(cloud_url)
        host = parsed_url.netloc

        return f"https://browser.{host}/?tab=active&vmId={vm_id}&os={os}&osVer={osVer}&bookingType=manual&browser={browser}&browserVer={browserVersion}&reconnect=true&reconnect=true"

    async def release_vm(self, vm_id: str, booking_id: str) -> dict:
        """
        Release a booked VM.

        Args:
            vm_id (str): The ID of the VM to release.
            booking_id (str): The ID of the booking to release.

        Returns:
            dict: API response with release details or error.
        """
        token = await auth_api.get_token()

        headers = {
            "Content-Type": "application/json",
            "Origin": cloud_url,
            "token": token,
        }

        payload = {"bookingId": booking_id}

        response = await self.post(
            constant.pclodyApiEndpoint.BOOK_VM + f"/{vm_id}/release",
            headers=headers,
            data=payload,
        )

        return response
