# PIF JSON Generator

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-GitHub%20Pages-blue?style=for-the-badge&logo=githubpages&logoColor=white)](https://azeolxc.github.io/PIF-JSON-Generator/)

[![CI Checks & Tests](https://github.com/AzeoLXC/PIF-JSON-Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/AzeoLXC/PIF-JSON-Generator/actions/workflows/ci.yml)
[![Auto-Generate PIF JSON Files](https://github.com/AzeoLXC/PIF-JSON-Generator/actions/workflows/auto_generate.yml/badge.svg)](https://github.com/AzeoLXC/PIF-JSON-Generator/actions/workflows/auto_generate.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Automated, resilient generator for **Play Integrity Fix (PIF) JSON** configuration files parsed directly from Android `system.prop` releases. Built with native retry backoffs, strict field validation, and automated CI/CD lifecycle workflows.

🌐 **Direct Access Live Dashboard:**  
👉 **[https://azeolxc.github.io/PIF-JSON-Generator/](https://azeolxc.github.io/PIF-JSON-Generator/)**

---

## Key Highlights

- 🌐 **Live Web Dashboard:** Real-time web explorer to browse and download PIF JSON configurations for both Stable and Experimental channels.
- 🛡️ **Resilient Network Adapter:** Engineered with `urllib3.util.Retry` exponential backoff (automatic recovery on `429`, `500`, `502`, `503`, and `504` HTTP status codes).
- ⚙️ **Dual Output Architectures:**
  - `extended` *(default)* — 19-field modern format with granular spoofing flags.
  - `legacy` — 8-field classic format for older PIF modules.
- 🧪 **Enterprise CI Pipeline:** Automated linting via `ruff`, full test suites via `pytest`, running on modern Node.js 24 native GitHub Action runners.
- 🔍 **Strict Schema Validation:** Automated parsing of API levels, security patch formats (`YYYY-MM-DD`), and build metadata before release.
- 🤖 **Zero-Touch Automation:** Runs unattended via GitHub Actions to sync, parse, validate, and publish releases.

---

## Architecture & Project Structure

```
PIF-JSON-Generator/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI: Ruff linter & Pytest suite
│       ├── pages.yml              # Deployment: GitHub Pages release dashboard
│       └── auto_generate.yml      # CD: Upstream watcher & release publisher
├── src/
│   └── pif_generator/
│       ├── __init__.py            # Package root & public exports
│       ├── core.py                # PIFGenerator core engine (Session + Retry)
│       └── constants.py           # Target props, schema definitions & fallbacks
├── tests/
│   ├── test_generator.py          # Pytest unit & mock integration tests
│   └── self_check.py              # Zero-dependency standalone verification
├── scripts/
│   ├── check_releases.py          # Upstream release tag polling
│   ├── generate_pifs.py           # Batch generator executor
│   └── publish_release.py         # Release packager & asset uploader
├── index.html                     # Live responsive release explorer dashboard
├── pyproject.toml                 # Modern PEP 621 / setuptools build config
├── requirements.txt               # Production & runtime dependencies
├── requirements-dev.txt           # Test & linting dependencies
└── LICENSE                        # MIT License
```

---

## Pipeline Workflow

```
[ Scheduled CRON / Dispatch ]
             │
             ▼
    check_releases.py       ── Query monitored upstream repos for new tags
             │
             ├─ (No new tag)  ── Terminate clean
             │
             ▼ (New tag detected)
     generate_pifs.py       ── Stream ZIPs via resilient retry session
             │              ── Extract system.prop in-memory
             │              ── Parse, transform & validate JSON schema
             ▼
    publish_release.py      ── Package artifacts & publish GitHub Release
             │
             ▼
       [ Git Sync ]         ── Persist processed release state tag
```

---

## Local Development & Testing

### 1. Installation

```bash
# Clone the repository
git clone git@github.com:AzeoLXC/PIF-JSON-Generator.git
cd PIF-JSON-Generator

# Install dependencies in editable mode
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### 2. Running Test Suites

Run the automated `pytest` suite:
```bash
pytest -v tests/
```

Or run the standalone self-check script (zero external test dependencies):
```bash
python tests/self_check.py
```

### 3. Code Quality & Linting

```bash
ruff check .
```

---

## Programmatic Usage

```python
from pathlib import Path
from src.pif_generator import PIFGenerator

# Initialize generator with custom parameters
generator = PIFGenerator(
    repo_type="stable",
    output_format="extended",
    output_dir=Path("./output"),
    http_timeout=120,
)

# Download, extract system.prop, validate and persist PIF JSON
output_path = generator.generate(
    zip_name="pixel_9_pro.zip",
    url="https://example.com/builds/pixel_9_pro.zip",
)

print(f"Generated PIF JSON: {output_path}")
```

---

## Output Formats

### Extended Format (Default)

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

### Legacy Format

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

## License

This project is licensed under the [MIT License](LICENSE).
