class AppError(Exception):
    """Base class for application-specific exceptions."""

    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)


class APIRequestError(AppError):
    """Raised when an API call fails"""

    def __init__(self, service: str, message: str = "API call failed", code: int = 502):
        full_message = f"{service} error: {message}"
        super().__init__(full_message, code)


class McpToolError(AppError):
    """Raised when something not working as expected in pcloudy mcp tools"""

    def __init__(self, tool: str, error: str, code: int = 501):
        message = f"{tool} error :  {error}"
        super().__init__(message, code)


class ServerInitializationError(AppError):
    """Raised when the server fails to initialize"""

    def __init__(self, stage: str, details: str, code: int = 503):
        message = f"Server initialization failed during '{stage}': {details}"
        super().__init__(message, code)


class AppStartupError(Exception):
    """Raised when the application fails to start due to a critical issue."""

    def __init__(self, stage: str, message: str):
        super().__init__(f"[StartupError:{stage}] {message}")
        self.stage = stage
        self.message = message
