import importlib.util
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "phase03_lora_manifest_contract_tests",
    API_ROOT / "tests" / "test_lora_dataset_manifest_contract.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

test_lora_dataset_manifest_uses_only_lora_qualified_derivatives = (
    MODULE.test_lora_dataset_manifest_uses_only_lora_qualified_derivatives
)
