# Phase
`phase_05_lora_training_registry_and_proof_generation`

## Scope
Truthful LoRA dataset selection, registry hardening, and blocked-state proof when the machine cannot perform a real AI Toolkit training/proof run.

## Files changed
- `apps/api/app/services/lora_training.py`
- `apps/api/app/services/prompt_expansion.py`
- `apps/api/tests/test_lora_dataset_selection.py`
- `apps/api/tests/test_lora_capability_and_registry.py`
- `apps/api/tests/test_lora_proof_image_contract.py`
- `tests/api/test_lora_dataset_selection.py`
- `tests/api/test_lora_capability_and_registry.py`
- `tests/api/test_lora_proof_image_contract.py`
- `docs/architecture/lora_dataset_and_proof_contract.md`
- `docs/verification/intake_saved_outputs_phase_05_blocker.md`

## Implementation summary
- Kept dataset selection pinned to LoRA-qualified assets by adding the exact Phase 05 verification entry point for:
  - dataset files + manifest version artifacts
  - exclusion of `body_only` and `rejected` entries
- Hardened the LoRA registry truth gate:
  - `current` entries now require a real artifact file
  - active-model resolution now returns `None` when the file is missing
  - the training payload reports `artifact-missing` instead of pretending the current model is still usable
  - generation workspace local-LoRA options now skip registry entries whose backing file is missing
- Added the exact Phase 05 verification entry points for:
  - truthful disabled capability when AI Toolkit is missing
  - registry/current-artifact truth
  - blocked proof-image behavior when generation runtime dependencies are unavailable
- Documented the combined dataset/proof contract and the exact runtime blocker evidence for this machine.

## Blocker summary
- AI Toolkit is not installed on this machine.
- ComfyUI proof-image generation is also not ready:
  - no `MEDIACREATOR_COMFYUI_BASE_URL`
  - no detected checkpoint files
  - no detected VAE files

## Status
BLOCKED
