import os
import json
import commentjson
import platform
from fastmcp import FastMCP
from typing import Dict, Any, Optional
from typing import Annotated
import sys


# Initialize MCP server
mcp = FastMCP("IDE config MCP Server")

# default is VS Code
ide = 'Code'

ideUserSettingMap = {
    "Code": {
        "Windows": os.path.expanduser("~\AppData\\Roaming\\Code\\User\\settings.json"),
        "Darwin": os.path.expanduser("~/Library/Application Support/Code/User/settings.json"),
        "Linux": os.path.expanduser("~/.config/Code/User/settings.json"),
    },
    "Cursor": {
        "Windows": os.path.expanduser("~\AppData\\Roaming\\Cursor\\User\\settings.json"),
        "Darwin": os.path.expanduser("~/Library/Application Support/Cursor/User/settings.json"),
        "Linux": os.path.expanduser("~/.config/Cursor/User/settings.json"),
    },
    "Trae": {
        "Windows": os.path.expanduser("~\AppData\\Roaming\\Trae\\User\\settings.json"),
        "Darwin": os.path.expanduser("~/Library/Application Support/Trae/User/settings.json"),
        "Linux": os.path.expanduser("~/.config/Trae/User/settings.json"),
    },
    "TraeCN": {
        "Windows": os.path.expanduser("~\AppData\\Roaming\\Trae CN\\User\\settings.json"),
        "Darwin": os.path.expanduser("~/Library/Application Support/Trae CN/User/settings.json"),
        "Linux": os.path.expanduser("~/.config/Trae CN/User/settings.json"),
    }
}

# Define IDE settings file path constants for different operating systems
WINDOWS_IDE_SETTINGS_PATH = os.path.expanduser("~\AppData\\Roaming\\Code\\User\\settings.json")
MACOS_IDE_SETTINGS_PATH = os.path.expanduser("~/Library/Application Support/Code/User/settings.json")
LINUX_IDE_SETTINGS_PATH = os.path.expanduser("~/.config/Code/User/settings.json")

# Set default IDE settings file path based on operating system
if platform.system() == "Windows":
    DEFAULT_IDE_SETTINGS_PATH = WINDOWS_IDE_SETTINGS_PATH
elif platform.system() == "Darwin":  # macOS
    DEFAULT_IDE_SETTINGS_PATH = MACOS_IDE_SETTINGS_PATH
elif platform.system() == "Linux":
    DEFAULT_IDE_SETTINGS_PATH = LINUX_IDE_SETTINGS_PATH
else:
    # Default to standard path for current operating system
    if os.name == "nt":  # Windows
        DEFAULT_IDE_SETTINGS_PATH = WINDOWS_IDE_SETTINGS_PATH
    else:  # Non-Windows systems default to Linux path
        DEFAULT_IDE_SETTINGS_PATH = LINUX_IDE_SETTINGS_PATH

# Ensure path format is correct
DEFAULT_IDE_SETTINGS_PATH = os.path.normpath(DEFAULT_IDE_SETTINGS_PATH)


def _get_ide_settings() -> Dict[str, Any]:
    """Get IDE user settings

    Returns:
        JSON content of the settings file
    """
    path = DEFAULT_IDE_SETTINGS_PATH
    try:
        if not os.path.exists(path):
            # If file doesn't exist, return empty dictionary
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            try:
                # Try to load commented JSON using commentjson
                return commentjson.load(f)
            except Exception as e:
                # If failed, try to load with standard json
                f.seek(0)
                try:
                    return json.load(f)
                except Exception:
                    return {'error': f' failed to parse JSON file: {str(e)}'}
    except Exception as e:
        return {"error": f" failed to read IDE settings file: {str(e)}"}

def _set_ide_settings(key: str, val: Any) -> Dict[str, Any]:
    """Set IDE user settings
    """
    path = DEFAULT_IDE_SETTINGS_PATH
    try:
        # Read existing settings
        current_settings = _get_ide_settings()
        # Update settings
        current_settings[key] = val
        # Write to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        return {"error": f" failed to update IDE settings file: {str(e)}"}

@mcp.tool(name = "get_ide_settings")
def get_ide_settings() -> Dict[str, Any]:
    """get all IDE user settings

    Args:

    Returns:
        IDE user settings
    """
    return _get_ide_settings()


@mcp.tool()
def update_ide_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """update IDE user settings

    Args:
        settings: Settings to update

    Returns:
        Updated settings file content
    """
    path = DEFAULT_IDE_SETTINGS_PATH
    try:
        # Read existing settings
        current_settings = get_ide_settings()
        # Update settings
        current_settings.update(settings)
        # Write to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
        return current_settings
    except Exception as e:
        return {"error": f" failed to update IDE settings file: {str(e)}"}



@mcp.tool()
def get_ide_setting_by_key(key: str) -> Dict[str, Any]:
    """Get IDE user setting by key, if not found in user settings, will return default value

    Args:
        key: Setting key name

    Returns:
        Dictionary containing setting value, or error message if key doesn't exist
    """
    try:
        # Get current settings
        current_settings = _get_ide_settings()
        # Check if key exists
        if key in current_settings:
            return {key: current_settings[key]}
        else:
            # If key not found in user settings, try to get default value from defaultSettings.json
            try:
                # Get default settings as string and parse with commentjson
                default_settings_str = _get_default_setttings()
                default_settings = commentjson.loads(default_settings_str)
                if key in default_settings:
                    return {key: default_settings[key]}
                return {"error": f" failed to find default setting for key: {key}"}
            except Exception:
                return {"error": f" failed to find default setting for key: {key}"}
    except Exception as e:
        return {"error": f" failed to get IDE setting for key: {key}, error: {str(e)}"}


@mcp.tool()
def set_ide_setting_by_key(
        key: Annotated[str, "the key of the setting"], 
        value: Annotated[Any, "the value of the setting"]
    ) -> Dict[str, Any]:
    """Set IDE user setting by key, if you're not sure about the setting key, you can get all available settings via get_default_settings tool or fetch https://code.visualstudio.com/docs/getstarted/settings

    Args:
        key: Setting key name
        value: New value for the setting

    Returns:
        Updated setting value, or error message if update failed
    """
    try:
        _set_ide_settings(key, value)
    except Exception as e:
        return {"error": f" failed to set IDE setting for key: {key}, error: {str(e)}"}
    return {key: value}

def _get_default_setttings() -> str:
    try:
        default_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'defaultSettings.json')
        if not os.path.exists(default_settings_path):
            return json.dumps({"error": "Default configuration file does not exist"})
        with open(default_settings_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return json.dumps({"error": f" failed to read default settings file: {str(e)}"})

@mcp.tool(
    name="get_default_settings",
    description="Get all available IDE settings and default value",
)
def get_default_settings() -> str:
    """Get all available IDE settings and default value
    
    Returns:
        IDE's default settings in json format with comments preserved
    """
    try:
        return _get_default_setttings()
    except Exception as e:
        return json.dumps({"error": f" failed to get default settings: {str(e)}"})

def main():
    """Main entry point for the MCP server"""
    global ide
    global DEFAULT_IDE_SETTINGS_PATH
    if len(sys.argv) > 1:
        ide = sys.argv[1]
    print(f"Current OS: {platform.system()}, Current IDE: {ide}")
    DEFAULT_IDE_SETTINGS_PATH = ideUserSettingMap[ide][platform.system()]
    
    mcp.run(transport="stdio")

    # for debug only
    # mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")

if __name__ == "__main__":
    main()

 