from __future__ import annotations

import io
import json
import logging
import re
import zipfile
from pathlib import Path
from typing import Any

import requests

from .constants import (
    BRAND_KEY_LEGACY,
    BRAND_KEYS,
    BUILD_ID_KEYS,
    BUILD_TAGS_KEYS,
    BUILD_TYPE_KEYS,
    DEVICE_KEYS_EXTENDED,
    DEVICE_KEYS_LEGACY,
    FINGERPRINT_KEYS_EXTENDED,
    FINGERPRINT_KEYS_LEGACY,
    MANUFACTURER_KEY_LEGACY,
    MANUFACTURER_KEYS,
    MIN_API_LEVEL,
    MODEL_KEY_LEGACY,
    MODEL_KEYS,
    OUTPUT_PREFIX,
    PRODUCT_KEYS_EXTENDED,
    PRODUCT_KEYS_LEGACY,
    RELEASE_KEYS,
    REQUIRED_FIELDS_EXTENDED,
    REQUIRED_FIELDS_LEGACY,
    SDK_KEYS,
    SDK_KEYS_LEGACY,
    SECURITY_PATCH_KEYS,
)

logger = logging.getLogger(__name__)

Props = dict[str, str]
PifData = dict[str, Any]


class PIFGenerator:

    def __init__(
        self,
        repo_type: str = "stable",
        output_format: str = "extended",
        output_dir: Path | None = None,
        http_timeout: int = 120,
    ) -> None:
        if repo_type not in OUTPUT_PREFIX:
            raise ValueError(f"Unknown repo_type {repo_type!r}. Expected: {list(OUTPUT_PREFIX)}")
        if output_format not in ("legacy", "extended"):
            raise ValueError(f"Unknown output_format {output_format!r}. Expected: 'legacy' or 'extended'")

        self.repo_type = repo_type
        self.output_format = output_format
        self.output_dir = output_dir or Path.cwd()
        self.http_timeout = http_timeout
        self._prefix = OUTPUT_PREFIX[repo_type]

    def generate(self, zip_name: str, url: str) -> Path:
        raw_content = self._download_and_extract(url)
        props = self._parse_system_prop(raw_content)
        logger.debug("Parsed %d properties from %s", len(props), zip_name)

        pif = self._build_pif(props)
        output_path = self._persist(zip_name, pif)

        logger.info("Generated → %s", output_path)
        return output_path

    @staticmethod
    def _parse_system_prop(content: str) -> Props:
        props: Props = {}
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            props[key.strip()] = value.strip()
        return props

    @staticmethod
    def _resolve_prop(props: Props, keys: list[str], default: str = "") -> str:
        for key in keys:
            value = props.get(key, "").strip()
            if value:
                return value
        return default

    def _download_and_extract(self, url: str) -> str:
        logger.info("Downloading %s", url)
        response = requests.get(url, timeout=self.http_timeout)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            for entry_name in archive.namelist():
                if entry_name.endswith("system.prop"):
                    logger.debug("Found system.prop → %s", entry_name)
                    return archive.read(entry_name).decode("utf-8")

        raise FileNotFoundError(f"system.prop not found in ZIP: {url}")

    def _extract_security_patch_from_metadata(
        self, fingerprint: str, build_id: str
    ) -> str:
        pattern = re.compile(r"\.(\d{2})(\d{2})(\d{2})\.")

        for source in (build_id, fingerprint):
            if not source:
                continue
            match = pattern.search(source)
            if match:
                year, month, day = match.groups()
                return f"20{year}-{month}-{day}"

        return ""

    def _build_pif(self, props: Props) -> PifData:
        if self.output_format == "legacy":
            pif = self._build_legacy_pif(props)
        else:
            pif = self._build_extended_pif(props)

        self._validate_pif(pif)
        return pif

    def _build_legacy_pif(self, props: Props) -> PifData:
        fingerprint = self._resolve_prop(props, FINGERPRINT_KEYS_LEGACY)
        if not fingerprint:
            raise ValueError("No fingerprint found in system.prop")

        first_api_level = self._resolve_prop(props, SDK_KEYS_LEGACY, default="0")

        return {
            "MANUFACTURER": props.get(MANUFACTURER_KEY_LEGACY, "Google").strip(),
            "MODEL":        props.get(MODEL_KEY_LEGACY, "Unknown").strip(),
            "FINGERPRINT":  fingerprint,
            "BRAND":        props.get(BRAND_KEY_LEGACY, "google").strip(),
            "PRODUCT":      self._resolve_prop(props, PRODUCT_KEYS_LEGACY),
            "DEVICE":       self._resolve_prop(props, DEVICE_KEYS_LEGACY),
            "SECURITY_PATCH": self._resolve_prop(props, SECURITY_PATCH_KEYS),
            "FIRST_API_LEVEL": str(int(first_api_level)),
        }

    def _build_extended_pif(self, props: Props) -> PifData:
        fingerprint = self._resolve_prop(props, FINGERPRINT_KEYS_EXTENDED)
        if not fingerprint:
            raise ValueError("No fingerprint found in system.prop")

        build_id = self._resolve_prop(props, BUILD_ID_KEYS)
        if not build_id:
            raise ValueError("No build ID found in system.prop")

        security_patch = self._resolve_prop(props, SECURITY_PATCH_KEYS)
        if not security_patch:
            security_patch = self._extract_security_patch_from_metadata(fingerprint, build_id)

        build_type = self._resolve_prop(props, BUILD_TYPE_KEYS, default="user")
        debuggable  = props.get("ro.debuggable", "0").strip()
        is_debug    = build_type in {"userdebug", "eng"} or debuggable == "1"

        device_initial_sdk = self._resolve_prop(props, SDK_KEYS, default="0")

        return {
            "ID":                   build_id,
            "BRAND":                self._resolve_prop(props, BRAND_KEYS, default="google"),
            "DEVICE":               self._resolve_prop(props, DEVICE_KEYS_EXTENDED),
            "MANUFACTURER":         self._resolve_prop(props, MANUFACTURER_KEYS, default="Google"),
            "FINGERPRINT":          fingerprint,
            "MODEL":                self._resolve_prop(props, MODEL_KEYS, default="Unknown"),
            "PRODUCT":              self._resolve_prop(props, PRODUCT_KEYS_EXTENDED),
            "SECURITY_PATCH":       security_patch,
            "DEVICE_INITIAL_SDK_INT": str(int(device_initial_sdk)),
            "TYPE":                 build_type,
            "TAG":                  self._resolve_prop(props, BUILD_TAGS_KEYS, default="release-keys"),
            "RELEASE":              self._resolve_prop(props, RELEASE_KEYS),
            "DEBUG":                is_debug,
            "spoofBuild":           "1",
            "spoofProps":           "0",
            "spoofProvider":        "0",
            "spoofSignature":       "0",
            "spoofVendingSdk":      "0",
            "verboseLogs":          "0",
        }

    def _validate_pif(self, pif: PifData) -> None:
        required = (
            REQUIRED_FIELDS_EXTENDED
            if self.output_format == "extended"
            else REQUIRED_FIELDS_LEGACY
        )

        for field in required:
            value = pif.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field}' is empty or missing")

        self._validate_api_level(pif, "FIRST_API_LEVEL")
        self._validate_api_level(pif, "DEVICE_INITIAL_SDK_INT")
        self._validate_security_patch(pif.get("SECURITY_PATCH", ""))

    @staticmethod
    def _validate_api_level(pif: PifData, field: str) -> None:
        raw = pif.get(field)
        if raw is None:
            return
        try:
            level = int(raw)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"'{field}' must be a valid integer, got: {raw!r}") from exc
        if level < MIN_API_LEVEL:
            raise ValueError(f"'{field}' is {level}, minimum is {MIN_API_LEVEL} (Android 5.0)")

    @staticmethod
    def _validate_security_patch(value: str) -> None:
        if value and len(value) != 10:
            raise ValueError(f"SECURITY_PATCH must be YYYY-MM-DD, got: {value!r}")

    def _persist(self, zip_name: str, pif: PifData) -> Path:
        stem = zip_name.removesuffix(".zip")
        filename = f"{self._prefix}{stem}.json"
        output_path = self.output_dir / filename
        output_path.write_text(json.dumps(pif, indent=2), encoding="utf-8")
        return output_path