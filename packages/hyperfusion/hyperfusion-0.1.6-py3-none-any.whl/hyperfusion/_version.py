"""Version information for hyperfusion."""

import os
import subprocess
import re


def get_version_from_git():
    """Get version from git tags or fallback to development version."""
    try:
        # Try to get version from git describe
        result = subprocess.run(
            ['git', 'describe', '--tags', '--always', '--dirty'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        
        # If it's a clean tag (no additional commits), use it directly
        if re.match(r'^v?\d+\.\d+\.\d+$', version):
            return version.lstrip('v')
        
        # If it's a development version, format it properly
        # e.g., "v0.1.0-5-g1234567" becomes "0.1.0.dev5+g1234567"
        match = re.match(r'^v?(\d+\.\d+\.\d+)-(\d+)-g([a-f0-9]+)(-dirty)?$', version)
        if match:
            base_version, commits, sha, dirty = match.groups()
            dev_version = f"{base_version}.dev{commits}+g{sha}"
            if dirty:
                dev_version += ".dirty"
            return dev_version
        
        # Fallback for other cases
        return f"0.1.0.dev0+{version}"
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback when git is not available or not in a git repository
        return os.environ.get('HYPERFUSION_VERSION', '0.1.0.dev0')


__version__ = get_version_from_git()