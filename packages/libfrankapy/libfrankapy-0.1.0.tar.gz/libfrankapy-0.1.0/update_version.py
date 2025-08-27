#!/usr/bin/env python3
"""Version update utility script.

This script helps update version numbers across project files to keep them in sync
with git tags before creating a release.
"""

import argparse
import re
import sys
from pathlib import Path


def update_version_in_file(
    file_path: Path, pattern: str, replacement: str, version: str
) -> bool:
    """Update version in a specific file.

    Args:
        file_path: Path to the file to update
        pattern: Regex pattern to find the version
        replacement: Replacement string with {version} placeholder
        version: New version number

    Returns:
        True if file was updated, False otherwise
    """
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        new_content = re.sub(pattern, replacement.format(version=version), content)

        if content != new_content:
            file_path.write_text(new_content, encoding="utf-8")
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def validate_version(version: str) -> bool:
    """Validate version format (semantic versioning)."""
    pattern = r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?$"
    return bool(re.match(pattern, version))


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Update version numbers across project files"
    )
    parser.add_argument("version", help="New version number (e.g., 1.0.0)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    args = parser.parse_args()

    # Validate version format
    if not validate_version(args.version):
        print(f"❌ Invalid version format: {args.version}")
        print("Version should follow semantic versioning (e.g., 1.0.0, 1.0.0-alpha.1)")
        sys.exit(1)

    print(f"🔄 Updating version to: {args.version}")

    if args.dry_run:
        print("🔍 DRY RUN - No files will be modified")

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir

    # Files to update with their patterns
    files_to_update = [
        {
            "path": project_root / "pyproject.toml",
            "pattern": r'^version = ".*"',
            "replacement": 'version = "{version}"',
        },
        {
            "path": project_root / "libfrankapy" / "__init__.py",
            "pattern": r'__version__ = ".*"',
            "replacement": '__version__ = "{version}"',
        },
    ]

    updated_files = 0

    for file_info in files_to_update:
        if args.dry_run:
            print(f"Would update: {file_info['path']}")
        else:
            if update_version_in_file(
                file_info["path"],
                file_info["pattern"],
                file_info["replacement"],
                args.version,
            ):
                updated_files += 1

    if args.dry_run:
        print(
            f"\n🔍 Dry run completed. {len(files_to_update)} files would be processed."
        )
    else:
        print(f"\n✅ Version update completed. {updated_files} files updated.")
        print(f"\n📝 Next steps:")
        print(f"   1. Review the changes: git diff")
        print(
            f"   2. Commit the changes: git add . && git commit -m 'chore: bump version to {args.version}'"
        )
        print(
            f"   3. Create and push tag: git tag v{args.version} && git push origin v{args.version}"
        )
        print(f"   4. GitHub Actions will automatically build and publish the release")


if __name__ == "__main__":
    main()
