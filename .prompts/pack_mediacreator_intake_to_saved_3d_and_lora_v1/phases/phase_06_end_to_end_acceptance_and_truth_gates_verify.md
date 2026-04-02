# Phase 06 verify — End-to-end acceptance and truth gates

## Verify goal

Prove that the full user journey is repeatable and that the app cannot lie about completion.

## Mandatory verification order

1. read the paired build file
2. run targeted truth-guard tests
3. run the end-to-end intake/3D flow
4. run the end-to-end LoRA/proof flow if capability is real
5. repeat the flow with a second run
6. update final acceptance documentation

## Exact verification steps

### Verify step 1
Prove a stale `complete` status with a missing file is surfaced as failure/incomplete, not success.

### Verify step 2
Prove the operator can:
- enter a duplicate label
- upload photos
- see progress
- inspect a thumbnail
- create a saved character
- reach a real saved GLB

### Verify step 3
When capability is real, prove the operator can reach:
- real LoRA artifact
- real proof image

### Verify step 4
Repeat the flow and prove both outputs remain independently valid.

## Exact commands Codex should run

- `pytest -q tests/api/test_output_truth_guards.py`
- `pnpm exec playwright test tests/e2e/intake_to_saved_character.spec.ts`
- `pnpm exec playwright test tests/e2e/intake_to_saved_character_repeat_run.spec.ts`
- `pytest -q tests/api/test_full_lora_proof_flow.py`
- `make lint`
- `make typecheck`

## Deterministic pass conditions

Phase 06 is PASS only if:
- truth guards catch missing-artifact false completion
- the end-to-end saved-character flow succeeds
- the repeat run succeeds
- when LoRA capability is real, the saved artifact and proof image both exist
- final acceptance docs include exact commands, artifact paths, and outcomes

## Deterministic fail conditions

Phase 06 is FAIL if:
- any false completion escapes the truth guard
- the flow requires hidden manual cleanup or intervention
- the second run regresses the first
- final acceptance docs omit exact evidence

## Deterministic blocked conditions

Phase 06 is BLOCKED only if:
- a required real dependency prevents completion, and
- the blocker report is explicit enough for a human to act on immediately
