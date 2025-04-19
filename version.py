#!/usr/bin/env python3
import re
import sys
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Try to import tomli/tomli_w or fallback to built-in tomllib in Python 3.11+
try:
    import tomli
    import tomli_w
except ImportError:
    try:
        import tomllib as tomli
        # If tomllib is available but tomli_w isn't, we'll handle writing differently
        tomli_w = None
    except ImportError:
        print("Error: Required dependencies not found. Please install with:")
        print("  uv pip install tomli tomli-w")
        print("Or run this script with:")
        print("  uv run ./version.py")
        sys.exit(1)

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch numbers."""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    numbers = list(map(int, match.groups()))
    if len(numbers) != 3:
        raise ValueError("Version must have exactly three components")

    return (numbers[0], numbers[1], numbers[2])

def increment_version(version: str, branch_type: str) -> str:
    """Increment version based on branch type.
    
    Args:
        version: Current version string (e.g., "1.2.3")
        branch_type: Type of branch ('feature', 'bugfix', or None)
        
    Returns:
        New version string or unchanged version if branch_type is not recognized
    """
    major, minor, patch = parse_version(version)

    if branch_type == 'feature':
        minor += 1
        patch = 0  # Reset patch version when incrementing minor version
    elif branch_type == 'bugfix':
        patch += 1
    else:
        return version  # No change for other branch types

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
    if tomli_w:
        # Use tomli_w if available
        pyproject_path.write_text(tomli_w.dumps(data))
    else:
        # Fallback for Python 3.11+ with tomllib but no tomli_w
        # This is a simple implementation that preserves the version
        content = pyproject_path.read_text()
        content = re.sub(
            r'version\s*=\s*["\']([^"\']+)["\']',
            f'version = "{new_version}"',
            content
        )
        pyproject_path.write_text(content)

def get_merge_source_branch() -> Optional[str]:
    """Get the source branch of the last merge.
    
    Returns:
        The branch type ('feature', 'bugfix') or None if not determinable
    """
    try:
        # Get the last merge commit details
        result = subprocess.run(
            ['git', 'log', '--merges', '-1', '--pretty=format:%s'],
            capture_output=True,
            text=True,
            check=True
        )
        merge_title = result.stdout.strip()
        
        # Parse the merge title to extract the source branch
        # Common format: "Merge branch 'feature/xyz' into 'main'"
        # or "Merge pull request #123 from user/feature/xyz"
        branch_name = None
        
        if 'from' in merge_title:
            # Extract branch name after 'from'
            parts = merge_title.split('from')[1].strip().split()
            if parts:
                branch_name = parts[0].strip("'\"")
        elif "branch '" in merge_title:
            # Extract branch name between quotes
            start = merge_title.find("branch '") + 8
            end = merge_title.find("'", start)
            if start > 7 and end > start:
                branch_name = merge_title[start:end]
                
        if not branch_name:
            return None
            
        # Determine branch type
        if 'feature/' in branch_name or '/feature/' in branch_name:
            return 'feature'
        elif 'bugfix/' in branch_name or '/bugfix/' in branch_name or 'fix/' in branch_name or '/fix/' in branch_name:
            return 'bugfix'
        
        return None
    except subprocess.CalledProcessError:
        return None

def main():
    try:
        # Define paths
        project_root = Path(__file__).parent
        init_path = project_root / 'zencrc' / '__init__.py'
        pyproject_path = project_root / 'pyproject.toml'

        # Check if files exist
        if not init_path.exists():
            print(f"Error: {init_path} not found")
            sys.exit(1)
            
        if not pyproject_path.exists():
            print(f"Error: {pyproject_path} not found")
            sys.exit(1)

        # Get source branch of the last merge
        branch_type = get_merge_source_branch()
        if not branch_type:
            print("No feature or bugfix branch detected in the last merge")
            print("No version change needed")
            sys.exit(0)

        # Get current version from pyproject.toml
        try:
            data = tomli.loads(pyproject_path.read_text())
            if 'project' not in data or 'version' not in data['project']:
                print("Error: Version not found in pyproject.toml")
                sys.exit(1)
                
            current_version = data['project']['version']
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")
            sys.exit(1)

        # Calculate new version
        new_version = increment_version(current_version, branch_type)

        if new_version == current_version:
            print("No version change needed")
            sys.exit(0)

        # Update files
        try:
            update_init_version(init_path, new_version)
            update_pyproject_version(pyproject_path, new_version)

            print(f"Version updated: {current_version} -> {new_version}")

            # Stage the changes
            subprocess.run(['git', 'add', str(init_path), str(pyproject_path)], check=True)
            subprocess.run(['git', 'commit', '-m', f'chore: bump version to {new_version}'], check=True)
        except Exception as e:
            print(f"Error updating version: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
