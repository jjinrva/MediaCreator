import importlib.util
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "phase04_saved_3d_output_tests",
    API_ROOT / "tests" / "test_saved_3d_output_contract.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

test_saved_base_glb_is_queued_then_registered_from_a_real_artifact = (
    MODULE.test_saved_base_glb_is_queued_then_registered_from_a_real_artifact
)
test_high_detail_path_uses_body_qualified_threshold_for_detail_prep = (
    MODULE.test_high_detail_path_uses_body_qualified_threshold_for_detail_prep
)
