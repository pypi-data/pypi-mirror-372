"""Tools configuration file.

This file defines which tools are enabled.
"""

# Format: (module_name, registration_function_name)
ENABLED_TOOLS = [
    ("device_booking", "device_booking_management"),
    ("browser_booking", "browser_booking_management"),
    ("qpilot", "qpilot_management"),
    ("app_management", "app_management"),
]

# Exported symbols
__all__ = [
    "ENABLED_TOOLS",
]
