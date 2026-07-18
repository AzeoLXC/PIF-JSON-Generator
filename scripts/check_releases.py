#!/usr/bin/env python3

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from github import Auth, Github, GithubException

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pif_generator.constants import MONITORED_REPOS

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)


def _read_last_tag(repo_type: str) -> str:
    tag_file = Path(f"last_release_{repo_type}_tag.txt")
    return tag_file.read_text(encoding="utf-8").strip() if tag_file.exists() else ""


def _write_github_output(key: str, value: str) -> None:
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")


def check_releases(github_token: str, force: bool = False) -> dict:
    client = Github(auth=Auth.Token(github_token))
    new_results: list[dict] = []

    for repo_config in MONITORED_REPOS:
        repo_slug = f"{repo_config['owner']}/{repo_config['name']}"
        repo_type = repo_config["type"]

        try:
            repo = client.get_repo(repo_slug)
        except GithubException as exc:
            logger.error("Could not access repo %s: %s", repo_slug, exc)
            continue

        try:
            latest_release = repo.get_latest_release()
        except GithubException:
            logger.warning("No published releases found for %s", repo_slug)
            continue

        tag = latest_release.tag_name
        last_processed_tag = _read_last_tag(repo_type)

        if not force and last_processed_tag == tag:
            logger.info("%s @ %s — already processed, skipping", repo_slug, tag)
            continue

        zip_assets = [
            {"name": asset.name, "url": asset.browser_download_url}
            for asset in latest_release.get_assets()
            if asset.name.endswith(".zip")
        ]

        if not zip_assets:
            logger.warning("%s @ %s — no ZIP assets found, skipping", repo_slug, tag)
            continue

        logger.info("[NEW] %s @ %s — %d asset(s)", repo_slug, tag, len(zip_assets))
        new_results.append(
            {
                "repo_type":  repo_type,
                "latest_tag": tag,
                "assets":     zip_assets,
                "count":      len(zip_assets),
            }
        )

    if new_results:
        logger.info("Found %d new release(s)", len(new_results))
        _write_github_output("new_release", "true")
        _write_github_output("results", json.dumps(new_results))
        return {"new_release": True, "results": new_results}

    logger.info("No new releases detected")
    _write_github_output("new_release", "false")
    return {"new_release": False, "results": []}


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN environment variable is not set")
        sys.exit(1)

    force = os.environ.get("FORCE_CHECK", "false").lower() == "true"
    result = check_releases(token, force=force)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()