from pathlib import Path
from typing import Dict, Optional

import toml

class ConfigFileNotFound(Exception):
    pass

class MissingConfiguration(Exception):
    """Configuration not present."""
    pass

def get_config_file_path(file_name: str = "pyproject.toml") -> Path:
    """Get config file path. If not found raise exception."""
    directory = Path.cwd()
    while not directory.joinpath(file_name).exists():
        if directory == directory.parent:
            raise ConfigFileNotFound(f"Config file {file_name} not found.")
        directory = directory.parent
    return directory.joinpath(file_name).resolve()

def get_config_dict(config_file_name: Optional[str] = None) -> Dict:
    """Get config dict."""
    if config_file_name:
        config_file_path = get_config_file_path(config_file_name)
    else:
        config_file_path = get_config_file_path()

    return toml.load(config_file_path)

def get_section(config_dict: Dict, scope_key: Optional[str]) -> Dict:
    """Get section from config dict."""
    tool_key = "tool"
    aiware_key = "aiware-codegen"
    
    if tool_key in config_dict and aiware_key in config_dict[tool_key]:
        if not scope_key:
            return config_dict[tool_key][aiware_key]

        if scope_key in config_dict[tool_key][aiware_key]:
            return config_dict[tool_key][aiware_key][scope_key]
        
        raise MissingConfiguration(f"Config has no [{tool_key}.{aiware_key}.{scope_key}] section.")

    raise MissingConfiguration(f"Config has no [{tool_key}.{aiware_key}] section.")
