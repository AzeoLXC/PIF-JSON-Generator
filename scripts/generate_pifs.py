#!/usr/bin/env python3

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pif_generator import PIFGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

GENERATED_FILES_MANIFEST = Path("generated_files.txt")


def generate_all(assets: list[dict], repo_type: str) -> tuple[list[str], list[str]]:
    generator = PIFGenerator(repo_type=repo_type)
    generated: list[str] = []
    failed: list[str] = []

    total = len(assets)
    for index, asset in enumerate(assets, start=1):
        asset_name = asset["name"]
        asset_url  = asset["url"]

        logger.info("[%d/%d] Processing %s", index, total, asset_name)

        try:
            output_path = generator.generate(asset_name, asset_url)
            generated.append(str(output_path))

            data: dict = json.loads(output_path.read_text(encoding="utf-8"))
            empty_fields = [k for k, v in data.items() if v is None or v == ""]
            if empty_fields:
                logger.warning("Empty fields in %s: %s", output_path.name, empty_fields)
            else:
                logger.info("Verified %s — all fields populated", output_path.name)

        except Exception as exc:
            logger.error("Failed to process %s: %s", asset_name, exc)
            failed.append(asset_name)

    return generated, failed


def _print_summary(generated: list[str], failed: list[str], total: int) -> None:
    separator = "=" * 60
    logger.info(separator)
    logger.info("SUCCESS: %d / %d", len(generated), total)
    logger.info("FAILED:  %d / %d", len(failed), total)
    logger.info(separator)
    if failed:
        logger.info("Failed assets:")
        for name in failed:
            logger.info("  • %s", name)


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: generate_pifs.py <assets_json> <repo_type>", file=sys.stderr)
        sys.exit(1)

    try:
        assets: list[dict] = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        logger.error("Invalid assets JSON: %s", exc)
        sys.exit(1)

    repo_type = sys.argv[2]

    logger.info("Processing %d asset(s) for repo_type=%r", len(assets), repo_type)

    generated, failed = generate_all(assets, repo_type)
    _print_summary(generated, failed, len(assets))

    if not generated:
        logger.error("No PIF files were generated — aborting")
        sys.exit(1)

    GENERATED_FILES_MANIFEST.write_text("\n".join(generated), encoding="utf-8")
    logger.info("Manifest written → %s", GENERATED_FILES_MANIFEST)


if __name__ == "__main__":
    main()