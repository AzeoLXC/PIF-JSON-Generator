from __future__ import annotations

MONITORED_REPOS: list[dict[str, str]] = [
    {"owner": "Pixel-Props",  "name": "build.prop",      "type": "stable"},
    {"owner": "Elcapitanoe",  "name": "Build-Prop-BETA", "type": "experimental"},
]

OUTPUT_PREFIX: dict[str, str] = {
    "stable":       "stable_pif_",
    "experimental": "experimental_pif_",
}

FINGERPRINT_KEYS_EXTENDED: list[str] = [
    "ro.system_ext.build.fingerprint",
    "ro.system.build.fingerprint",
    "ro.build.fingerprint",
    "ro.product.build.fingerprint",
    "ro.bootimage.build.fingerprint",
    "ro.vendor.build.fingerprint",
    "ro.system_dlkm.build.fingerprint",
]

FINGERPRINT_KEYS_LEGACY: list[str] = [
    "ro.build.fingerprint",
    "ro.product.build.fingerprint",
    "ro.bootimage.build.fingerprint",
    "ro.vendor.build.fingerprint",
    "ro.system.build.fingerprint",
]

BUILD_ID_KEYS: list[str] = [
    "ro.system_ext.build.id",
    "ro.system.build.id",
    "ro.build.id",
    "ro.vendor.build.id",
    "ro.system_dlkm.build.id",
]

PRODUCT_KEYS_EXTENDED: list[str] = [
    "ro.product.system_ext.name",
    "ro.product.system.name",
    "ro.product.name",
    "ro.build.product",
    "ro.product.system_ext.device",
    "ro.product.device",
    "ro.product.board",
]

PRODUCT_KEYS_LEGACY: list[str] = [
    "ro.build.product",
    "ro.product.device",
    "ro.product.name",
    "ro.product.board",
]

DEVICE_KEYS_EXTENDED: list[str] = [
    "ro.product.system_ext.device",
    "ro.product.system.device",
    "ro.product.device",
    "ro.build.product",
    "ro.product.board",
]

DEVICE_KEYS_LEGACY: list[str] = [
    "ro.product.device",
    "ro.build.product",
    "ro.product.board",
]

BRAND_KEYS: list[str] = [
    "ro.product.system_ext.brand",
    "ro.product.system.brand",
    "ro.product.brand",
]

MANUFACTURER_KEYS: list[str] = [
    "ro.product.system_ext.manufacturer",
    "ro.product.system.manufacturer",
    "ro.product.manufacturer",
]

MODEL_KEYS: list[str] = [
    "ro.product.system_ext.model",
    "ro.product.system.model",
    "ro.product.model",
]

SDK_KEYS: list[str] = [
    "ro.product.first_api_level",
    "ro.board.first_api_level",
    "ro.board.api_level",
    "ro.system_ext.build.version.sdk",
    "ro.system.build.version.sdk",
    "ro.build.version.sdk",
]

SDK_KEYS_LEGACY: list[str] = [
    "ro.product.first_api_level",
    "ro.board.first_api_level",
    "ro.board.api_level",
    "ro.build.version.sdk",
    "ro.system.build.version.sdk",
]

BUILD_TYPE_KEYS: list[str] = [
    "ro.system_ext.build.type",
    "ro.system.build.type",
    "ro.build.type",
]

BUILD_TAGS_KEYS: list[str] = [
    "ro.system_ext.build.tags",
    "ro.system.build.tags",
    "ro.build.tags",
]

RELEASE_KEYS: list[str] = [
    "ro.system_ext.build.version.release",
    "ro.system.build.version.release",
    "ro.build.version.release",
    "ro.build.version.release_or_codename",
]

SECURITY_PATCH_KEYS: list[str] = [
    "ro.build.version.security_patch",
    "ro.vendor.build.security_patch",
]

MANUFACTURER_KEY_LEGACY = "ro.product.manufacturer"
MODEL_KEY_LEGACY         = "ro.product.model"
BRAND_KEY_LEGACY         = "ro.product.brand"

REQUIRED_FIELDS_LEGACY: list[str] = [
    "MANUFACTURER", "MODEL", "FINGERPRINT", "BRAND", "PRODUCT", "DEVICE",
]

REQUIRED_FIELDS_EXTENDED: list[str] = [
    "ID", "MANUFACTURER", "MODEL", "FINGERPRINT", "BRAND", "PRODUCT", "DEVICE",
]

MIN_API_LEVEL = 21