import importlib.util
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "phase04_character_creation_tests",
    API_ROOT / "tests" / "test_character_creation_from_classified_photoset.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

test_character_creation_is_acceptance_gated_and_preserves_bucket_lineage = (
    MODULE.test_character_creation_is_acceptance_gated_and_preserves_bucket_lineage
)
test_character_creation_fails_when_all_images_are_rejected = (
    MODULE.test_character_creation_fails_when_all_images_are_rejected
)
