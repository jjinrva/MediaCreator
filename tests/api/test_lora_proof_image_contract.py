import importlib.util
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "phase05_lora_proof_contract_tests",
    API_ROOT / "tests" / "test_lora_proof_image_contract.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

test_lora_proof_generation_stays_truthful_when_runtime_dependencies_are_missing = (
    MODULE.test_lora_proof_generation_stays_truthful_when_runtime_dependencies_are_missing
)
