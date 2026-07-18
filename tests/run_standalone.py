import sys
import tempfile
from pathlib import Path

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_generator import (
    MockResponse,
    mock_zip_bytes,
    sample_props_content,
    test_build_extended_pif,
    test_build_legacy_pif,
    test_generate_from_zip,
    test_parse_system_prop,
    test_validation_missing_field,
)


class DummyMonkey:

    def setattr(self, target, attr, value):
        setattr(target, attr, value)


if __name__ == "__main__":
    print("Executing PIF-JSON-Generator standalone test suite...")
    sample = sample_props_content()
    mock_zip = mock_zip_bytes(sample)

    test_parse_system_prop(sample)
    print("  [PASS] test_parse_system_prop")

    tmp = Path(tempfile.mkdtemp())
    test_build_extended_pif(sample, tmp)
    print("  [PASS] test_build_extended_pif")

    test_build_legacy_pif(sample, tmp)
    print("  [PASS] test_build_legacy_pif")

    test_generate_from_zip(mock_zip, tmp, DummyMonkey())
    print("  [PASS] test_generate_from_zip")

    test_validation_missing_field(tmp)
    print("  [PASS] test_validation_missing_field")

    print("\nALL 5 TESTS PASSED SUCCESSFULLY!")
