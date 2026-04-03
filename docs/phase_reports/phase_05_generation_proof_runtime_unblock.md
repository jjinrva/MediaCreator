# Phase 05 generation proof runtime unblock

## Status

PASS

## Scope

Add the missing proof-image execution path, keep blocked generation truthful when runtime
dependencies are absent, and prevent placeholder ComfyUI workflows from reporting `ready`.

## Files changed

- `apps/api/app/services/jobs.py`
- `apps/api/app/services/generation_execution.py`
- `apps/api/app/services/generation_provider.py`
- `apps/api/app/services/prompt_expansion.py`
- `apps/api/app/api/routes/generation.py`
- `apps/api/app/schemas/generation.py`
- `apps/api/app/schemas/system.py`
- `apps/api/tests/test_generation_provider.py`
- `apps/api/tests/test_lora_proof_image_contract.py`
- `docs/verification/phase_05_generation_proof_runtime_unblock_verify.md`
- `docs/verification/final_verify_matrix.md`
- `docs/verification/final_verify_matrix.json`
- `docs/handoff/overnight_acceptance_report.md`

## Implementation summary

- Added a real `generation-proof-image` job payload and queue path for ready image requests.
- Added a dedicated provider execution service that calls the ComfyUI `/prompt`, `/history`,
  and `/view` contract, then refuses success unless a real image file exists on disk.
- Added an explicit worker branch that completes the job only after storage-object persistence
  and request/character lineage are written.
- Tightened generation readiness so placeholder workflow files with `nodes: []` stay blocked.
- Updated generation request payloads to expose proof-image job state and artifact state truthfully.

## Notes

- The repo-level workflow files under `workflows/comfyui/` remain placeholders on purpose, so
  the live machine stays blocked until validated graphs are installed under the configured
  `MEDIACREATOR_COMFYUI_WORKFLOWS_ROOT`.
- A targeted Phase 05 verify pass now proves the ready path with a real saved PNG artifact and
  persisted lineage in a deterministic test runtime.
