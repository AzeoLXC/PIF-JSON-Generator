# PIF JSON Generator

[![Auto-Generate PIF JSON Files](https://github.com/AzeoLXC/PIF-JSON-Generator/actions/workflows/auto_generate.yml/badge.svg)](https://github.com/AzeoLXC/PIF-JSON-Generator/actions/workflows/auto_generate.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Automated generator of **Play Integrity Fix (PIF) JSON** property files from the latest Android build-property releases. New upstream releases are detected every 6 hours via GitHub Actions; JSON files are generated and attached to a GitHub release automatically.

---

## Features

- Supports **two output formats**:
  - `legacy` — 8-field format (original PIF spec)
  - `extended` *(default)* — 19-field format with spoofing flags
- Property resolution follows **strict source priority** (e.g. `system_ext` → `system` → generic)
- Security patch date is **derived automatically** from the build ID when not explicitly set
- Full field **validation** before any file is written
- Runs fully **unattended** via GitHub Actions on a 6-hour schedule

---

## Project Structure

```
PIF-JSON-Generator/
├── .github/
│   └── workflows/
│       └── auto_generate.yml   # CI/CD: detect → generate → publish
├── src/
│   └── pif_generator/
│       ├── __init__.py          # Public API surface
│       ├── core.py              # PIFGenerator class
│       └── constants.py         # Property key lists, repo config, validation rules
├── scripts/
│   ├── check_releases.py        # Query upstream repos for new releases
│   ├── generate_pifs.py         # Batch-generate PIF JSON from asset list
│   └── publish_release.py       # Create GitHub release & upload assets
├── pyproject.toml
├── requirements.txt
└── LICENSE
```

---

## How It Works

```
GitHub Actions (every 6 h)
        │
        ▼
check_releases.py   ── queries Pixel-Props & Elcapitanoe repos
        │                for the latest release tag
        │  new tag found?
        ▼
generate_pifs.py    ── downloads each ZIP, extracts system.prop,
        │                builds & validates PIF JSON
        ▼
publish_release.py  ── creates a GitHub release on this repo
        │                and uploads all generated JSON files
        ▼
git commit          ── persists the processed tag so the same
                         release is never processed twice
```

---

## Monitored Upstream Repositories

| Type           | Repository                                                        |
|----------------|-------------------------------------------------------------------|
| `stable`       | [Pixel-Props/build.prop](https://github.com/Pixel-Props/build.prop) |
| `experimental` | [Elcapitanoe/Build-Prop-BETA](https://github.com/Elcapitanoe/Build-Prop-BETA) |

---

## Local Usage

### Prerequisites

```bash
pip install -r requirements.txt
```

### Generate a single PIF (ad-hoc)

```python
from src.pif_generator import PIFGenerator

generator = PIFGenerator(repo_type="stable", output_format="extended")
output = generator.generate("pixel_9_ap4a.zip", "https://example.com/pixel_9_ap4a.zip")
print(f"Written → {output}")
```

### Run the full pipeline manually

```bash
export GITHUB_TOKEN="ghp_..."

# 1. Check for new releases
python scripts/check_releases.py

# 2. Generate PIF files (replace with actual JSON from step 1)
python scripts/generate_pifs.py '[{"name":"pixel_9.zip","url":"https://..."}]' stable

# 3. Publish release
python scripts/publish_release.py owner/repo v2025-10-05 stable
```

---

## Output Formats

### Extended (default)

```json
{
  "ID": "BP3A.241005.015",
  "BRAND": "google",
  "DEVICE": "caiman",
  "MANUFACTURER": "Google",
  "FINGERPRINT": "google/caiman/caiman:15/BP3A.241005.015/...",
  "MODEL": "Pixel 9 Pro",
  "PRODUCT": "caiman",
  "SECURITY_PATCH": "2024-10-05",
  "DEVICE_INITIAL_SDK_INT": "35",
  "TYPE": "user",
  "TAG": "release-keys",
  "RELEASE": "15",
  "DEBUG": false,
  "spoofBuild": "1",
  "spoofProps": "0",
  "spoofProvider": "0",
  "spoofSignature": "0",
  "spoofVendingSdk": "0",
  "verboseLogs": "0"
}
```

### Legacy

```json
{
  "MANUFACTURER": "Google",
  "MODEL": "Pixel 9 Pro",
  "FINGERPRINT": "google/caiman/caiman:15/BP3A.241005.015/...",
  "BRAND": "google",
  "PRODUCT": "caiman",
  "DEVICE": "caiman",
  "SECURITY_PATCH": "2024-10-05",
  "FIRST_API_LEVEL": "35"
}
```

---

## Credits

- Build property data — [Pixel-Props/build.prop](https://github.com/Pixel-Props/build.prop)
- Experimental firmware properties — [Elcapitanoe/Build-Prop-BETA](https://github.com/Elcapitanoe/Build-Prop-BETA)
- Workflow and tooling — Prateek Maru, 2025

## License

Released under the [MIT License](LICENSE).