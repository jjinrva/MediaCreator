# Phase 02 verify — Frontend intake truth, label, and thumbnail preview

## Verify goal

Prove that the intake UI is no longer misleading and that thumbnail inspection is usable.

## Mandatory verification order

1. read the paired build file
2. run targeted frontend/unit checks first
3. run targeted Playwright flows for intake and thumbnail preview
4. run broader lint/type checks
5. update `docs/verification/intake_saved_outputs_phase_02_verify.md`

## Exact verification steps

### Verify step 1
Prove the label field blocks upload when empty and allows a duplicate label.

### Verify step 2
Prove transfer progress is shown and the generic indefinite upload message is gone.

### Verify step 3
Prove server-side stage progress and bucket counts appear before character creation is enabled.

### Verify step 4
Prove clicking a thumbnail opens a larger preview dialog with bucket/reason details.

### Verify step 5
Prove `body_only`, `lora_only`, `both`, and `rejected` are rendered as distinct visible groups or counts.

## Exact commands Codex should run

- `pnpm test -- CharacterImportIngest`
- `pnpm exec playwright test tests/e2e/character_intake_truth.spec.ts`
- `pnpm exec playwright test tests/e2e/character_thumbnail_preview.spec.ts`
- `make lint`
- `make typecheck`

## Deterministic pass conditions

Phase 02 is PASS only if:

- the empty-label path is blocked
- duplicate labels are accepted
- progress state is stage-aware
- the create action stays disabled until ingest completes with accepted images
- the enlarged preview dialog works by mouse and keyboard
- the verify report contains exact evidence

## Deterministic fail conditions

Phase 02 is FAIL if:

- the page can still sit on a vague upload message
- the thumbnail preview dialog is missing or inaccessible
- bucket summaries are missing or collapsed into one generic accepted state
- the verify report is incomplete
