import io
import json
import zipfile
from pathlib import Path
import pytest

from pif_generator import PIFGenerator


@pytest.fixture
def sample_props_content() -> str:
    return """
ro.build.id=UP1A.231005.007
ro.build.fingerprint=google/cheetah/cheetah:14/UP1A.231005.007/10754064:user/release-keys
ro.product.brand=google
ro.product.model=Pixel 7 Pro
ro.product.device=cheetah
ro.product.name=cheetah
ro.product.manufacturer=Google
ro.build.version.security_patch=2023-10-05
ro.build.version.sdk=34
ro.build.type=user
ro.build.tags=release-keys
ro.build.version.release=14
"""


@pytest.fixture
def mock_zip_bytes(sample_props_content: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("system.prop", sample_props_content)
    return buffer.getvalue()


class MockResponse:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_parse_system_prop(sample_props_content: str) -> None:
    props = PIFGenerator._parse_system_prop(sample_props_content)
    assert props["ro.build.id"] == "UP1A.231005.007"
    assert props["ro.product.model"] == "Pixel 7 Pro"
    assert props["ro.product.brand"] == "google"


def test_build_extended_pif(sample_props_content: str, tmp_path: Path) -> None:
    generator = PIFGenerator(repo_type="stable", output_format="extended", output_dir=tmp_path)
    props = generator._parse_system_prop(sample_props_content)
    pif = generator._build_extended_pif(props)

    assert pif["ID"] == "UP1A.231005.007"
    assert pif["BRAND"] == "google"
    assert pif["MODEL"] == "Pixel 7 Pro"
    assert pif["DEVICE"] == "cheetah"
    assert pif["SECURITY_PATCH"] == "2023-10-05"
    assert pif["DEVICE_INITIAL_SDK_INT"] == "34"
    assert pif["spoofBuild"] == "1"


def test_build_legacy_pif(sample_props_content: str, tmp_path: Path) -> None:
    generator = PIFGenerator(repo_type="stable", output_format="legacy", output_dir=tmp_path)
    props = generator._parse_system_prop(sample_props_content)
    pif = generator._build_legacy_pif(props)

    assert pif["MANUFACTURER"] == "Google"
    assert pif["MODEL"] == "Pixel 7 Pro"
    assert pif["FINGERPRINT"].startswith("google/cheetah/cheetah:14")
    assert pif["SECURITY_PATCH"] == "2023-10-05"


def test_generate_from_zip(mock_zip_bytes: bytes, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    generator = PIFGenerator(repo_type="stable", output_format="extended", output_dir=tmp_path)

    # Mock HTTP session get
    monkeypatch.setattr(generator.session, "get", lambda url, timeout: MockResponse(mock_zip_bytes))

    out_file = generator.generate("cheetah.zip", "https://example.com/cheetah.zip")
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["MODEL"] == "Pixel 7 Pro"
    assert data["BRAND"] == "google"


def test_validation_missing_field(tmp_path: Path) -> None:
    generator = PIFGenerator(repo_type="stable", output_format="extended", output_dir=tmp_path)
    invalid_props = "ro.build.id=TEST\n"  # missing fingerprint

    props = generator._parse_system_prop(invalid_props)
    with pytest.raises(ValueError, match="No fingerprint found"):
        generator._build_extended_pif(props)
