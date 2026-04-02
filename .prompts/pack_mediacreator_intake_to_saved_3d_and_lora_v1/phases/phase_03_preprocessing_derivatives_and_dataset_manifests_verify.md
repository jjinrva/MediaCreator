# Phase 03 verify — Preprocessing derivatives and dataset manifests

## Verify goal

Prove that body and LoRA downstream inputs are explicit, bounded, and lineage-safe.

## Mandatory verification order

1. read the paired build file
2. run targeted derivative and manifest tests
3. inspect written files and metadata
4. run lint/type checks
5. update `docs/verification/intake_saved_outputs_phase_03_verify.md`

## Exact verification steps

### Verify step 1
Assert normalized derivatives exist for person-qualified inputs.

### Verify step 2
Assert body derivatives exist for `body_only` and `both`, and do not exist for non-body buckets.

### Verify step 3
Assert LoRA derivatives and manifests include only `lora_only` and `both`.

### Verify step 4
Assert originals remain intact and lineage metadata points to all derivative paths.

## Exact commands Codex should run

- `pytest -q tests/api/test_photo_derivatives_and_manifests.py`
- `pytest -q tests/api/test_lora_dataset_manifest_contract.py`
- `make lint`
- `make typecheck`

## Deterministic pass conditions

Phase 03 is PASS only if:
- derivative files exist in the correct places
- manifests reference only allowed buckets
- lineage links are persisted
- verify output lists exact checked files and paths

## Deterministic fail conditions

Phase 03 is FAIL if:
- originals were overwritten
- bucket leakage occurs
- manifests are incomplete
- the verify report lacks exact artifact evidence
