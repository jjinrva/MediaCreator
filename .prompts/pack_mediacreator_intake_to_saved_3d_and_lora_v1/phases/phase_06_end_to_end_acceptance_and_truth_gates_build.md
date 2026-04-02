# Phase 06 build — End-to-end acceptance and truth gates

## Phase goal

Lock the operator journey with deterministic end-to-end checks and forbid misleading completion states.

## Experts Codex must use for this phase

- `/experts/QA_VERIFICATION_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`

## Exact chosen path

- Add targeted end-to-end API and Playwright coverage for the full intake-to-output path.
- Add a shared artifact-existence guard that the UI/API uses before surfacing complete/ready/generated states.
- Run the operator journey twice from clean or isolated test state.
- Produce a final PASS/FAIL/BLOCKED report. No softer wording.

## Exact stack and libraries

- pytest / TestClient
- Playwright
- file existence checks
- database/output assertions

### Source IDs for this phase
S03, S04, S05, S06, S12, S14

## Exact file areas

Start with these areas:

- API tests created in earlier phases
- Playwright specs created in earlier phases
- any shared status/output helpers that mark jobs complete
- scripts or helpers used to verify saved artifacts

## Ordered steps

### Step 1 — create shared truth guards

Wherever completion is surfaced, require a common guard that checks:
- status field
- artifact existence
- registry/output row existence

Do not trust status text alone.

**Verification immediately after Step 1**
- add tests that simulate a missing file with a stale complete status and prove the UI/API reports failure or incomplete instead

### Step 2 — end-to-end intake and 3D acceptance flow

Run one complete flow:
- label entered
- photos uploaded
- progress observed
- classification summary shown
- thumbnail enlarged
- character created
- saved GLB produced

**Verification immediately after Step 2**
- add or refine one Playwright flow that covers this full path

### Step 3 — end-to-end LoRA acceptance flow

Run one complete LoRA flow:
- LoRA dataset created from valid buckets
- capability checked
- LoRA artifact registered when capability is real
- proof image generated when capability is real

**Verification immediately after Step 3**
- add one API or mixed API/UI proof path that asserts real outputs

### Step 4 — repeatability run

Repeat the operator flow with a different photoset or isolated fixture set and confirm:
- duplicate label still works
- acceptance gating still works
- saved outputs are independently addressable

**Verification immediately after Step 4**
- update final acceptance report with both run identifiers

## Pass/fail criteria

### PASS
- full operator flow passes
- complete states are guarded by artifact existence
- duplicate labels still work
- repeat run does not regress the first run

### FAIL
- any complete state is shown without an artifact
- end-to-end flow depends on hidden manual intervention
- second run breaks duplicate-label or saved-output behavior

## Deliverables

- shared truth guard
- end-to-end API/UI coverage
- final acceptance report
- blocker report if capability prevents real completion

## Forbidden scope

- do not replace targeted tests with screenshots
- do not skip the repeatability run
- do not downgrade FAIL to PASS because “most of it works”

## Documentation Codex must update in this phase

- `docs/phase_reports/intake_saved_outputs_phase_06.md`
- `docs/verification/intake_saved_outputs_phase_06_verify.md`
- `docs/verification/intake_saved_outputs_final_acceptance.md`

## Exit condition

The pack may stop only with one of these outcomes:

- PASS with complete evidence
- FAIL with exact broken step
- BLOCKED with exact dependency/runtime blocker
