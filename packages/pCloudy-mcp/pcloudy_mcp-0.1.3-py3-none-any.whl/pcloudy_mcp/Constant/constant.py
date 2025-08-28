from urllib.parse import urlparse

from ..utils.config import Config

config = Config()
base_url = config.userdetail.pcloudy_cloud_url


class McpServer:
    """
    This class represents the MCP server configuration for the pCloudy MCP application.
    It includes server name and version.
    """

    SERVER_NAME = "pCloudy-mcp-tool"
    SERVER_VERSION = "0.1.0"


class QpilotServerEndpoints:
    """This class contains the QPilot server endpoints."""

    production_host = [
        "ind-west.pcloudy.com",
        "us.pcloudy.com",
        "sg.pcloudy.com",
        "ind-west2.pcloudy.com",
        "uae.pcloudy.com",
    ]

    SERVER_GROUPS = {
        "https://dev-backend.qpilot.pcloudy.com": [
            "node-stg.pcloudy.com",
            "node-stg-sub.pcloudy.com",
        ],
        "https://stg-backend.qpilot.pcloudy.com": [
            "staging.pcloudy.com",
            "staging-sub.pcloudy.com",
        ],
        "https://prod-backend.qpilot.pcloudy.com": [
            "device.pcloudy.com",
            "ind-west.pcloudy.com",
            "us.pcloudy.com",
            "sg.pcloudy.com",
            "uae.pcloudy.com",
        ],
        "https://qa-private-backend.qpilot.pcloudy.com": [
            "private-test-main.pcloudy.com",
            "private-test-sub.pcloudy.com",
        ],
    }

    # Invert the structure for fast hostname-to-URL lookup
    HOST_TO_QPILOT_SERVER = {
        host: url for url, host_list in SERVER_GROUPS.items() for host in host_list
    }

    @classmethod
    def get_qpilot_origin(cls):
        parsed_url = urlparse(base_url)
        return (
            "https://device.pcloudy.com"
            if parsed_url.hostname in cls.production_host
            else base_url
        )

    @classmethod
    def get_qpilot_server(cls) -> str:
        hostname = urlparse(base_url).hostname
        return cls.HOST_TO_QPILOT_SERVER.get(
            hostname,
            "https://prod-private-backend.qpilot.pcloudy.com",  # default fallback
        )


class BrowserCloud:
    """This class maps BrowserCloud URLs to their backend servers."""

    SERVER_GROUPS = {
        "https://qa-backend.browser.pcloudy.com": [
            "device.pcloudy.com",
        ],
        "https://adcb-qat-backend.browser.pcloudy.com": [
            "adcb-qat.pcloudy.com",
        ],
        "https://franklin-backend.browser.pcloudy.com": [
            "franklin.pcloudy.com",
        ],
        "20.197.33.157": [  # direct IP backend
            "gehealthcare.pcloudy.com",
        ],
        "https://manulife-backend.browser.pcloudy.com": [
            "manulife.pcloudy.com",
        ],
        "https://mgm-backend.browser.pcloudy.com": [
            "mgm.pcloudy.com",
        ],
        "https://private-poc-backend.browser.pcloudy.com": [
            "private-poc.pcloudy.com",
        ],
        "https://ship-hats-backend.browser.pcloudy.com": [
            "ship-hats.pcloudy.com",
        ],
        "https://slb-backend.browser.pcloudy.com": [
            "slb.pcloudy.com",
        ],
        "https://wizbank-backend-browser.pcloudy.com": [
            "wizbank.pcloudy.com",
        ],
        "https://dev-backend.browser.pcloudy.com": [
            "node-stg.pcloudy.com",
        ],
        "https://prod-backend.browser.pcloudy.com": [
            "staging.pcloudy.com",
        ],
        "https://qa-private-backend.browser.pcloudy.com": [
            "private-test-main.pcloudy.com",
        ],
        "https://prod-private-backend.browser.pcloudy.com": [
            "private-live.pcloudy.com",
        ],
    }

    # Invert mapping: hostname → backend
    HOST_TO_BACKEND = {
        host: backend for backend, hosts in SERVER_GROUPS.items() for host in hosts
    }

    @classmethod
    def get_backend_url(cls) -> str:
        """
        Uses the global base_url and returns the backend URL.
        """
        parsed_url = urlparse(base_url)
        hostname = parsed_url.hostname
        return cls.HOST_TO_BACKEND.get(
            hostname,
            "https://prod-private-backend.browser.pcloudy.com",  # default fallback
        )


class PcloudyApiEndpoints:
    """
    This class contains the API endpoints for pCloudy.
    """

    AUTHENTICATE = f"{base_url}/api/access"
    GET_DEVICE_LIST = f"{base_url}/api/devices"
    BOOK_DEVICE = f"{base_url}/api/book_device"
    LIVE_VIEW_URL = f"{base_url}/api/get_device_url"
    RELEASE_DEVICE = f"{base_url}/api/release_device"
    UPLOAD_APP = f"{base_url}/api/upload_file"
    AVALIABLE_APPS = f"{base_url}/api/drive"
    INSTALL_AND_LAUNCH_APP = f"{base_url}/api/install_app"
    INITIATE_IOS_RESIGN = f"{base_url}/api/resign/initiate"
    PROGRESS_IOS_RESIGN = f"{base_url}/api/resign/progress"
    DOWNLOAD_IOS_RESIGN = f"{base_url}/api/resign/download"

    # Browser Cloud
    GET_VMS = f"{BrowserCloud.get_backend_url()}/api/v1/get-vms"
    BOOK_VM = f"{BrowserCloud.get_backend_url()}/api/v1"

    # QPilot Endpoints
    GET_CREDIT_BALANCE = f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/get-qpilot-credits-left"
    GET_PROJECT_LIST = (
        f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/project/fetch"
    )
    CREATE_PROJECT = (
        f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/project/create"
    )
    GET_TESTSUITE_LIST = (
        f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/get-test-suites"
    )
    CREATE_TESTSUITE = (
        f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/create-test-suite"
    )
    GET_TESTCASE_LIST = (
        f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/get-tests"
    )
    CREATE_TESTCASE = (
        f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/create-test-case"
    )
    START_WDA_IOS = f"{base_url}/api/v2/qpilot/wda/control"
    START_APPIUM = f"{base_url}/api/v2/qpilot/appium/control"
    GENERATE_CODE = f"{base_url}/api/v2/qpilot/generate-code"
    GENERATE_CODE_BROWSER = f"{QpilotServerEndpoints.get_qpilot_server()}/api/v1/qpilot/generate-test-script"


class HttpRetryConfig:
    """
    This class contains the retry configuration for HTTP requests.
    """

    MAX_RETRIES = 3
    WAIT_SECONDS = 2
    TIMEOUT = 180.0  # timeout in seconds


class Constant:
    """
    This class contains constant values used throughout the pCloudy MCP application.
    """

    mcpServer = McpServer()
    pclodyApiEndpoint = PcloudyApiEndpoints()
    httpRetryConfig = HttpRetryConfig()
    qpilot = QpilotServerEndpoints()
    TOKEN_CACHE_NAMESPACE = "pcloudy_tokens"
    TOKEN_CACHE_TTL = 5 * 24 * 60 * 60
    DURATION_TO_BOOK_DEVICE = 30  # in minutes, can be changed as per requirement
    MAXIMUM_RETRIES_RESIGN_PROGRESS = 20
