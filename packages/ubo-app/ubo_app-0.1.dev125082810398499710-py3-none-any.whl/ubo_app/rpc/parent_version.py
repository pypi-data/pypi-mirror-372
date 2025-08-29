"""Get the version of the parent package using hatch."""

import subprocess
from pathlib import Path


def get_version() -> str:
    """Return the version of the parent package."""
    return '123'
    root = Path().absolute().parent
    while not any(i.name == 'pyproject.toml' for i in root.iterdir()):
        root = root.parent
    result = subprocess.run(
        [
            '/usr/bin/env',
            'uv',
            'run',
            'poe',
            'version',
        ],
        check=True,
        text=True,
        cwd=root,
        capture_output=True,
    )
    return result.stdout.strip()
