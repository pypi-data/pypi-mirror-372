"""
Version checking utilities for the Kapso CLI.
"""
import requests
from packaging import version
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

CACHE_FILE = Path.home() / ".kapso" / "version_cache.json"
CACHE_HOURS = 24
VERSION_CHECK_URL = "https://app.kapso.ai/api/cli/version"

# Define the version here - update this when releasing
__version__ = "0.1.0"


def get_current_version() -> str:
    """Get currently installed version."""
    try:
        # Try to import from the installed package
        from importlib.metadata import version as get_version
        return get_version("kapso")
    except:
        # Fallback to hardcoded version for development
        return __version__


def _read_cache() -> Optional[Dict[str, str]]:
    """Read cache file. Returns None if invalid or expired."""
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
        
        # Check if cache is expired
        cached_time = datetime.fromisoformat(data['timestamp'])
        if datetime.now() - cached_time > timedelta(hours=CACHE_HOURS):
            return None
            
        return data
    except:
        return None


def _write_cache(latest_version: str, update_command: str) -> None:
    """Write to cache file."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CACHE_FILE, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'latest_version': latest_version,
            'update_command': update_command
        }, f)


def check_for_update(force: bool = False) -> Optional[Dict[str, str]]:
    """
    Check if update is available. Returns None if check fails.
    
    Args:
        force: Force fresh check, ignoring cache
        
    Returns:
        Dict with update info if update available, None otherwise
    """
    current = get_current_version()
    
    # Check cache first (unless forced)
    if not force:
        cache = _read_cache()
        if cache:
            latest = cache.get('latest_version')
            if latest and version.parse(current) < version.parse(latest):
                return {
                    "current": current,
                    "latest": latest,
                    "command": cache.get('update_command', 'pip install --upgrade kapso')
                }
            return None
    
    # Make API call
    try:
        response = requests.get(
            VERSION_CHECK_URL,
            timeout=2,
            headers={'User-Agent': f'kapso-cli/{current}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            latest = data.get("latest_version")
            command = data.get("update_command", "pip install --upgrade kapso")
            
            if latest:
                # Update cache
                _write_cache(latest, command)
                
                if version.parse(current) < version.parse(latest):
                    return {
                        "current": current,
                        "latest": latest,
                        "command": command
                    }
    except:
        pass  # Fail silently
    
    return None