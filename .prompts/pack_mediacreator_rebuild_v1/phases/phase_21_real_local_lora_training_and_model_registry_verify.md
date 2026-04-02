# Phase 21 verify — Real local LoRA training, model registry, and activation

## Verify goal

Prove that Phase 21 is working the way the build document required. Do not accept screenshots or vague statements as proof. Use commands, API assertions, UI assertions, file assertions, and database checks where needed.

## Mandatory verification order

1. Read `AGENTS.md`
2. Read the paired build file for Phase 21
3. Read the expert files named in the build file
4. Run only the smallest set of tests needed to prove this phase first
5. If those pass, run broader lint/typecheck/regression checks if the phase requires them
6. Update `docs/verification/phase_21_verify.md`

## Exact verification steps

### Verify step 1
Run the capability check with AI Toolkit missing and confirm truthful disabled status.

### Verify step 2
If AI Toolkit is installed, run a small real training job and confirm output registration.

### Verify step 3
Confirm the model registry records current/working/failed states correctly.

### Verify step 4
Confirm the generation system can resolve an active LoRA artifact by registry lookup.


## Minimum commands Codex should run

- targeted backend tests for the changed domain
- targeted frontend unit tests for changed components
- targeted Playwright specs for changed user flows
- `make lint`
- `make typecheck`

If the phase introduces a long-running job or exported artifact, add a focused job/output test before broad regression checks.

## Pass criteria

Phase 21 is PASS only if:
- all required targeted checks pass,
- the feature behaves truthfully in the UI,
- database state matches UI/API state where relevant,
- required files/outputs exist where relevant,
- the verify report is updated with exact evidence.

## Fail criteria

Phase 21 is FAIL if:
- any required targeted test fails,
- the UI shows fake or misleading state,
- the database does not reflect the operation,
- an artifact is missing or mislabeled,
- the behavior only works once and fails on reload/retry,
- the verify report is incomplete.

## Required verify report content

Write these sections into `docs/verification/phase_21_verify.md`:
- Scope verified
- Commands run
- Files changed in the phase
- Results
- PASS/FAIL decision
- Remaining risks
