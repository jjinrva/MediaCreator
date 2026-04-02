import importlib.util
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "phase03_photo_derivatives_tests",
    API_ROOT / "tests" / "test_photo_derivatives_and_manifests.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

test_ingest_writes_bucket_bound_derivatives_and_explicit_manifests = (
    MODULE.test_ingest_writes_bucket_bound_derivatives_and_explicit_manifests
)
