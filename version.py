#!/usr/bin/env python3
import re
import sys
import tomli
import tomli_w
import subprocess
from pathlib import Path
from typing import Tuple, Optional

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch numbers."""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    numbers = list(map(int, match.groups()))
    if len(numbers) != 3:
        raise ValueError("Version must have exactly three components")

    return (numbers[0], numbers[1], numbers[2])

def increment_version(version: str, commit_msg: str) -> str:
    """Increment version based on commit message."""
    major, minor, patch = parse_version(version)

    if commit_msg.startswith('breaking:'):
        major += 1
        minor = 0
        patch = 0
    elif commit_msg.startswith('feat:'):
        minor += 1
        patch = 0
    elif commit_msg.startswith('patch:'):
        patch += 1
    else:
        return version

    return f"{major}.{minor}.{patch}"

def update_init_version(init_path: Path, new_version: str) -> None:
    """Update version in __init__.py file."""
    if not init_path.exists():
        raise FileNotFoundError(f"__init__.py not found at {init_path}")

    content = init_path.read_text()
    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )
    init_path.write_text(new_content)

def update_pyproject_version(pyproject_path: Path, new_version: str) -> None:
    """Update version in pyproject.toml file."""
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

    # Read TOML file
    data = tomli.loads(pyproject_path.read_text())

    # Update version
    if 'project' in data:
        data['project']['version'] = new_version

    # Write back to file
    pyproject_path.write_text(tomli_w.dumps(data))

def get_merge_commit_message() -> Optional[str]:
    """Get the merge commit message from git."""
    import subprocess

    try:
        # Get the last merge commit message
        result = subprocess.run(
            ['git', 'log', '--merges', '-1', '--pretty=format:%B'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def main():
    try:
        # Define paths
        project_root = Path(__file__).parent
        init_path = project_root / 'zencrc' / '__init__.py'
        pyproject_path = project_root / 'pyproject.toml'

        # Get merge commit message
        commit_msg = get_merge_commit_message()
        if not commit_msg:
            print("No merge commit message found")
            sys.exit(1)

        # Get current version from pyproject.toml
        data = tomli.loads(pyproject_path.read_text())
        current_version = data['project']['version']

        # Calculate new version
        new_version = increment_version(current_version, commit_msg.lower())

        if new_version == current_version:
            print("No version change needed")
            sys.exit(0)

        # Update files
        update_init_version(init_path, new_version)
        update_pyproject_version(pyproject_path, new_version)

        print(f"Version updated: {current_version} -> {new_version}")

        # Stage the changes
        subprocess.run(['git', 'add', str(init_path), str(pyproject_path)], check=True)
        subprocess.run(['git', 'commit', '-m', f'chore: bump version to {new_version}'], check=True)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
