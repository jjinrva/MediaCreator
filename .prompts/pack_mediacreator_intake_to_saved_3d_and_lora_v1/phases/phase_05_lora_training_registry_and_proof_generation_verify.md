# Phase 05 verify — LoRA training, registry, and proof generation

## Verify goal

Prove that the LoRA path is truthful and that proof-image success cannot be overstated.

## Mandatory verification order

1. read the paired build file
2. run dataset inclusion/exclusion tests
3. run capability-check tests
4. if capability is real, run the smallest real training/proof flow possible
5. update `docs/verification/intake_saved_outputs_phase_05_verify.md`

## Exact verification steps

### Verify step 1
Prove `body_only` and `rejected` assets are excluded from the LoRA dataset.

### Verify step 2
Prove capability is reported disabled when AI Toolkit is missing or misconfigured.

### Verify step 3
If capability is available, prove a real artifact is created and registered.

### Verify step 4
If capability is available, prove a real proof image is saved and linked to the artifact.

### Verify step 5
Prove no API/UI success state appears without the real artifact paths.

## Exact commands Codex should run

- `pytest -q tests/api/test_lora_dataset_selection.py`
- `pytest -q tests/api/test_lora_capability_and_registry.py`
- `pytest -q tests/api/test_lora_proof_image_contract.py`
- `make lint`
- `make typecheck`

If the environment can support a real training run, add the exact command used and the exact artifact path produced to the verify report.

## Deterministic pass conditions

Phase 05 is PASS only if:
- dataset selection is correct
- capability reporting is truthful
- the model registry reflects real artifact state
- a proof image exists when capability is real
- the verify report shows exact artifact paths

## Deterministic fail conditions

Phase 05 is FAIL if:
- dataset leakage occurs
- capability is guessed
- the artifact is missing
- the proof image is missing
- the verify report is incomplete

## Deterministic blocked conditions

Phase 05 is BLOCKED only if:
- the repo/runtime lacks the dependency needed for real training, and
- the blocker report contains exact failing commands and exact required next action
