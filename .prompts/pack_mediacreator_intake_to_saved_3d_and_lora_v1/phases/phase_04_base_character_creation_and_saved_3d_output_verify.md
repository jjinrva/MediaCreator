# Phase 04 verify — Base character creation and saved 3D output

## Verify goal

Prove that accepted assets create a saved character and a saved, artifact-backed 3D output.

## Mandatory verification order

1. read the paired build file
2. run targeted backend character/output tests
3. run targeted Playwright detail-page tests
4. run artifact existence checks
5. update `docs/verification/intake_saved_outputs_phase_04_verify.md`

## Exact verification steps

### Verify step 1
Prove character creation fails when all images are rejected and succeeds when at least one accepted asset exists.

### Verify step 2
Prove duplicate labels are allowed and do not collapse two different character IDs.

### Verify step 3
Prove the 3D route queues work instead of running it inline.

### Verify step 4
Prove a real GLB artifact exists before complete status is shown.

### Verify step 5
Prove the character detail page reload still resolves the saved GLB output.

## Exact commands Codex should run

- `pytest -q tests/api/test_character_creation_from_classified_photoset.py`
- `pytest -q tests/api/test_saved_3d_output_contract.py`
- `pnpm exec playwright test tests/e2e/character_detail_saved_glb.spec.ts`
- `make lint`
- `make typecheck`

## Deterministic pass conditions

Phase 04 is PASS only if:
- character creation is acceptance-gated
- duplicate labels are allowed
- queued job metadata is returned
- the GLB file exists and is registered
- the detail page reload resolves the saved output

## Deterministic fail conditions

Phase 04 is FAIL if:
- character creation uses rejected assets
- a “complete” state appears before file existence is proven
- the GLB disappears on reload
- the verify report lacks artifact proof
