#!/usr/bin/env python3

from __future__ import annotations

import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from github import Auth, Github, GithubException

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

GENERATED_FILES_MANIFEST = Path("generated_files.txt")


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

    release_tag  = f"{repo_type}-pif-{upstream_tag}"
    release_name = f"{repo_type.capitalize()} PIF — {upstream_tag}"
    release_body = (
        f"Auto-generated {len(file_paths)} PIF JSON file(s).\n"
        f"Source tag: `{upstream_tag}`  |  "
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d')}"
    )

    release = _get_or_create_release(repo, release_tag, release_name, release_body)

    existing_assets: dict[str, object] = {
        asset.name: asset for asset in release.get_assets()
    }

    uploaded = 0
    skipped  = 0
    errors   = 0

    for file_str in file_paths:
        filepath = Path(file_str)

        if not filepath.exists():
            logger.warning("File not found, skipping: %s", filepath)
            continue

        if filepath.name in existing_assets:
            logger.info("Already uploaded, skipping: %s", filepath.name)
            skipped += 1
            continue

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


def _get_or_create_release(repo, tag: str, name: str, body: str):
    try:
        release = repo.create_git_release(tag=tag, name=name, message=body)
        logger.info("Created release: %s", tag)
        return release
    except GithubException as exc:
        if exc.status == 422:
            release = repo.get_release(tag)
            logger.info("Release already exists, reusing: %s", tag)
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