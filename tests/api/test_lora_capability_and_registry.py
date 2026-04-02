import importlib.util
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2] / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "phase05_lora_capability_registry_tests",
    API_ROOT / "tests" / "test_lora_capability_and_registry.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

test_lora_training_route_reports_truthful_disabled_state_when_ai_toolkit_is_missing = (
    MODULE.test_lora_training_route_reports_truthful_disabled_state_when_ai_toolkit_is_missing
)
test_current_lora_registry_entries_require_real_artifacts_for_activation = (
    MODULE.test_current_lora_registry_entries_require_real_artifacts_for_activation
)
