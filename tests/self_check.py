import sys
from pathlib import Path

# Insert repo src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pif_generator.core import PIFGenerator

def run_tests():
    sample = """
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
    props = PIFGenerator._parse_system_prop(sample)
    assert props["ro.build.id"] == "UP1A.231005.007"
    assert props["ro.product.model"] == "Pixel 7 Pro"
    print("Test 1: parse_system_prop OK")

    gen = PIFGenerator(repo_type="stable", output_format="extended")
    pif = gen._build_extended_pif(props)
    assert pif["ID"] == "UP1A.231005.007"
    assert pif["BRAND"] == "google"
    assert pif["spoofBuild"] == "1"
    print("Test 2: build_extended_pif OK")

    legacy_gen = PIFGenerator(repo_type="stable", output_format="legacy")
    legacy_pif = legacy_gen._build_legacy_pif(props)
    assert legacy_pif["MANUFACTURER"] == "Google"
    assert legacy_pif["MODEL"] == "Pixel 7 Pro"
    print("Test 3: build_legacy_pif OK")

    # Test retry session creation
    assert hasattr(gen, "session")
    print("Test 4: resilient HTTP session OK")

if __name__ == "__main__":
    run_tests()
    print("ALL STANDALONE VERIFICATION PASSED")
