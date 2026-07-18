#!/usr/bin/env python3

from __future__ import annotations

import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from github import Auth, Github, GithubException

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

GENERATED_FILES_MANIFEST = Path("generated_files.txt")


def _format_calver_tag(upstream_tag: str, repo_type: str) -> tuple[str, str, bool]:
    """
    Format standard CalVer release tag and title.
    Example:
      upstream_tag='20260716', repo_type='experimental'
      -> tag: 'v2026.07.16-experimental'
      -> name: 'Experimental PIF (v2026.07.16)'
      -> prerelease: True
    """
    clean_tag = upstream_tag.lstrip("v")
    if len(clean_tag) == 8 and clean_tag.isdigit():
        formatted_date = f"{clean_tag[:4]}.{clean_tag[4:6]}.{clean_tag[6:]}"
    else:
        formatted_date = clean_tag

    if repo_type.lower() == "experimental":
        tag = f"v{formatted_date}-experimental"
        name = f"Experimental PIF — {formatted_date}"
        is_prerelease = True
    else:
        tag = f"v{formatted_date}"
        name = f"Stable PIF — {formatted_date}"
        is_prerelease = False

    return tag, name, is_prerelease


def publish_release(
    repo_name: str,
    upstream_tag: str,
    repo_type: str,
    file_paths: list[str],
) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN environment variable is not set")
        sys.exit(1)

    client = Github(auth=Auth.Token(token))
    repo   = client.get_repo(repo_name)

    release_tag, release_name, is_prerelease = _format_calver_tag(upstream_tag, repo_type)

    release_body = (
        f"### Play Integrity Fix JSON Artifacts\n\n"
        f"- **Channel:** `{repo_type.capitalize()}`\n"
        f"- **Upstream Source Tag:** `{upstream_tag}`\n"
        f"- **Total JSON Files:** `{len(file_paths)}`\n"
        f"- **Generated At:** `{datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}`\n\n"
        f"Download the appropriate JSON property file for your device and module configuration."
    )

    release = _get_or_create_release(repo, release_tag, release_name, release_body, is_prerelease)

    existing_assets: dict[str, Any] = {
        asset.name: asset for asset in release.get_assets()
    }

    force = os.environ.get("FORCE_CHECK", "false").lower() == "true"

    uploaded = 0
    skipped  = 0
    errors   = 0

    for file_str in file_paths:
        filepath = Path(file_str)

        if not filepath.exists():
            logger.warning("File not found, skipping: %s", filepath)
            continue

        if not force and filepath.name in existing_assets:
            logger.info("Already uploaded, skipping: %s", filepath.name)
            skipped += 1
            continue

        if force and filepath.name in existing_assets:
            logger.info("Force check active — replacing existing asset: %s", filepath.name)
            try:
                existing_assets[filepath.name].delete_asset()
            except Exception as e:
                logger.warning("Could not delete old asset %s: %s", filepath.name, e)

        try:
            logger.info("Uploading %s …", filepath.name)
            release.upload_asset(str(filepath))
            uploaded += 1
        except GithubException as exc:
            logger.error("Upload failed for %s: %s", filepath.name, exc)
            errors += 1

    logger.info(
        "Done — uploaded: %d  |  skipped: %d  |  errors: %d  |  total: %d",
        uploaded, skipped, errors, len(file_paths),
    )

    if errors:
        sys.exit(1)


def _get_or_create_release(repo: Any, tag: str, name: str, body: str, prerelease: bool) -> Any:
    try:
        release = repo.create_git_release(
            tag=tag,
            name=name,
            message=body,
            prerelease=prerelease,
        )
        logger.info("Created release: %s (prerelease=%s)", tag, prerelease)
        return release
    except GithubException as exc:
        if exc.status == 422:
            release = repo.get_release(tag)
            logger.info("Release already exists, reusing: %s", tag)
            # Ensure prerelease and name are synchronized
            try:
                release.update_release(name=name, message=body, prerelease=prerelease)
            except Exception:
                pass
            return release
        raise


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "Usage: publish_release.py <owner/repo> <upstream_tag> <repo_type>",
            file=sys.stderr,
        )
        sys.exit(1)

    repo_name    = sys.argv[1]
    upstream_tag = sys.argv[2]
    repo_type    = sys.argv[3]

    if not GENERATED_FILES_MANIFEST.exists():
        logger.error("Manifest not found: %s", GENERATED_FILES_MANIFEST)
        sys.exit(1)

    file_paths = [
        line for line in GENERATED_FILES_MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not file_paths:
        logger.error("Manifest is empty — nothing to upload")
        sys.exit(1)

    publish_release(repo_name, upstream_tag, repo_type, file_paths)


if __name__ == "__main__":
    main()
