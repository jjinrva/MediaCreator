# Phase
`phase_05_lora_training_registry_and_proof_generation`

## Scope verified
- dataset selection stays limited to `lora_only` and `both`
- dataset version artifacts and manifests are written
- AI Toolkit capability is reported as unavailable when the trainer is missing
- the registry cannot present a `current` LoRA without a real artifact file
- generation/proof requests remain staged and do not overstate success when the proof runtime is unavailable
- repo lint and typecheck pass after the Phase 05 truth-gate changes

## Commands run
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_lora_dataset_selection.py`
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_lora_capability_and_registry.py`
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_lora_proof_image_contract.py`
- `make -C /opt/MediaCreator lint`
- `make -C /opt/MediaCreator typecheck`

## Artifact and truth checks
- `tests/api/test_lora_dataset_selection.py` proved:
  - the dataset route writes image/caption files plus `dataset_manifest.json`
  - the manifest contains only LoRA-qualified derivatives
  - `body_only` and `rejected` inputs are excluded
- `tests/api/test_lora_capability_and_registry.py` proved:
  - missing AI Toolkit returns `capability.status = unavailable`
  - the training route refuses to queue when AI Toolkit is missing
  - `register_lora_model(..., status="current")` now rejects missing artifact files
  - deleting the backing file turns the registry payload into `artifact-missing`
  - missing-file rows are excluded from generation workspace local-LoRA options
- `tests/api/test_lora_proof_image_contract.py` proved:
  - a real current LoRA artifact can exist while generation capability is still unavailable
  - generation requests are stored as `status = staged` with `provider_status = unavailable`
  - no proof-image storage objects are created in that blocked state

## Results
- `pytest -q tests/api/test_lora_dataset_selection.py`: `2 passed`
- `pytest -q tests/api/test_lora_capability_and_registry.py`: `2 passed`
- `pytest -q tests/api/test_lora_proof_image_contract.py`: `1 passed`
- `make -C /opt/MediaCreator lint`: passed
- `make -C /opt/MediaCreator typecheck`: passed
  - note: mypy emitted the existing informational note `unused section(s): module = ['rembg.*']` without failing the command

## Blocker evidence
- Real training/proof verification could not run because this machine lacks the required runtime dependencies.
- Exact blocker details are recorded in:
  - `docs/verification/intake_saved_outputs_phase_05_blocker.md`

## PASS/FAIL/BLOCKED decision
BLOCKED

## Why this is blocked instead of failed
- The code and tests now keep the LoRA path truthful.
- The remaining gap is environmental, not a silent app failure:
  - AI Toolkit is absent
  - ComfyUI proof-image runtime is not configured with a base URL, checkpoints, and VAEs
