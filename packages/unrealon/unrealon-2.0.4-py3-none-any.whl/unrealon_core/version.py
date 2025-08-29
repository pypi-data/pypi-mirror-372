"""
🔄 UnrealOn Version Management

Unified version system for all UnrealOn packages.
This ensures version synchronization between driver, RPC server, and core components.
"""

import tomlkit
from typing import Dict, Any
from pathlib import Path
from unrealon_core.utils.time import utc_timestamp


def _get_version_from_pyproject() -> str:
    """Get version from main pyproject.toml."""
    try:
        # Go up from unrealon-core/src/unrealon_core to project root
        project_root = Path(__file__).parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "r") as f:
                pyproject = tomlkit.parse(f.read())
            
            # Try PEP 621 format first
            if "project" in pyproject and "version" in pyproject["project"]:
                return str(pyproject["project"]["version"])
            # Fallback to Poetry format
            elif "tool" in pyproject and "poetry" in pyproject["tool"] and "version" in pyproject["tool"]["poetry"]:
                return str(pyproject["tool"]["poetry"]["version"])
    except Exception:
        pass
    
    # Fallback version if can't read from pyproject.toml
    return "2.0.0"


# 🎯 UNIFIED VERSION - Automatically synced from main pyproject.toml
__version__ = _get_version_from_pyproject()

# 📅 Release Information
__release_date__ = "2024-12-19"
__build_number__ = "20241219001"

# 🏷️ Version Components
VERSION_MAJOR = 4
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_BUILD = "stable"

# 🔧 Package Compatibility Matrix
COMPATIBILITY_MATRIX = {
    "unrealon_core": __version__,
    "unrealon_rpc": __version__,
    "unrealon_driver": __version__,
    "unrealon_browser": __version__
}

# 📊 Version Metadata
VERSION_INFO = {
    "version": __version__,
    "major": VERSION_MAJOR,
    "minor": VERSION_MINOR,
    "patch": VERSION_PATCH,
    "build": VERSION_BUILD,
    "release_date": __release_date__,
    "build_number": __build_number__,
    "compatibility": COMPATIBILITY_MATRIX
}


def get_version() -> str:
    """
    Get the current UnrealOn version.
    
    Returns:
        str: Version string (e.g., "4.0.0")
    """
    return __version__


def get_version_info() -> Dict[str, Any]:
    """
    Get detailed version information.
    
    Returns:
        Dict[str, Any]: Complete version metadata
    """
    return VERSION_INFO.copy()


def get_build_info() -> Dict[str, Any]:
    """
    Get build information.
    
    Returns:
        Dict[str, Any]: Build metadata
    """
    return {
        "version": __version__,
        "build_number": __build_number__,
        "release_date": __release_date__,
        "build_type": VERSION_BUILD,
        "timestamp": utc_timestamp()
    }


def is_compatible_version(other_version: str) -> bool:
    """
    Check if another version is compatible with current version.
    
    Args:
        other_version: Version string to check
        
    Returns:
        bool: True if versions are compatible
    """
    try:
        # For now, require exact match for stability
        return other_version == __version__
    except Exception:
        return False


def get_compatibility_status(package_versions: Dict[str, str]) -> Dict[str, Any]:
    """
    Check compatibility status of multiple packages.
    
    Args:
        package_versions: Dict of package names to versions
        
    Returns:
        Dict[str, Any]: Compatibility report
    """
    compatible_packages = []
    incompatible_packages = []
    
    for package, version in package_versions.items():
        expected_version = COMPATIBILITY_MATRIX.get(package)
        if expected_version and version == expected_version:
            compatible_packages.append(package)
        else:
            incompatible_packages.append({
                "package": package,
                "current": version,
                "expected": expected_version
            })
    
    return {
        "overall_compatible": len(incompatible_packages) == 0,
        "compatible_packages": compatible_packages,
        "incompatible_packages": incompatible_packages,
        "total_packages": len(package_versions),
        "compatibility_score": len(compatible_packages) / len(package_versions) if package_versions else 1.0
    }


# 🎯 Convenience functions for specific packages
def get_core_version() -> str:
    """Get unrealon_core version."""
    return COMPATIBILITY_MATRIX["unrealon_core"]


def get_rpc_version() -> str:
    """Get unrealon_rpc version."""
    return COMPATIBILITY_MATRIX["unrealon_rpc"]


def get_driver_version() -> str:
    """Get unrealon_driver version."""
    return COMPATIBILITY_MATRIX["unrealon_driver"]


def get_browser_version() -> str:
    """Get unrealon_browser version."""
    return COMPATIBILITY_MATRIX["unrealon_browser"]


# 🔍 Version validation
def validate_version_format(version: str) -> bool:
    """
    Validate version string format.
    
    Args:
        version: Version string to validate
        
    Returns:
        bool: True if format is valid
    """
    try:
        parts = version.split(".")
        if len(parts) != 3:
            return False
        
        # Check if all parts are integers
        for part in parts:
            int(part)
        
        return True
    except (ValueError, AttributeError):
        return False


# 📋 Export all version functions
__all__ = [
    "__version__",
    "VERSION_INFO",
    "COMPATIBILITY_MATRIX",
    "get_version",
    "get_version_info", 
    "get_build_info",
    "is_compatible_version",
    "get_compatibility_status",
    "get_core_version",
    "get_rpc_version", 
    "get_driver_version",
    "get_browser_version",
    "validate_version_format"
]
