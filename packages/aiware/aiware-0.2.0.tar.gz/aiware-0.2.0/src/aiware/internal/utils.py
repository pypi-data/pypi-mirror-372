import os
from pathlib import Path


def get_package_root():
    """Find package root by looking for setup.py, pyproject.toml, or .git"""
    current = Path(__file__).parent
    
    while current != current.parent:
        if (current / 'aiware').exists():
            return current / 'aiware'
        current = current.parent
    
    raise RuntimeError("Could not find package root")

def get_relative_path(target_path: str):
    """Get path relative to package root"""
    package_root = get_package_root()
    return os.path.abspath(os.path.join(package_root, target_path))
