# Phase 05 build — regression verification and docs alignment

## Goal
Finish the repair pack by aligning tests, docs, and runtime contracts.

## Exact decisions
- update tests to the new host/origin strategy
- add focused regression coverage for the repaired flow
- update README/operator docs to explain the actual flow
- remove stale `10.0.0.102` examples from runtime docs

## Files to inspect and edit
- `README.md`
- `docs/handoff/operator_runbook.md`
- `docs/verification/*` as needed
- `apps/web/playwright.config.js`
- `apps/web/tests/unit/*` affected by API base changes
- `apps/web/tests/e2e/*` affected by runtime changes
- `apps/api/tests/*` affected by async route semantics

## Exact steps
1. Update runtime docs to explain:
   - bind host vs browser host
   - upload/QC is immediate
   - preview/reconstruction/training/video are queued jobs
   - worker heartbeat matters
2. Update tests to stop assuming one fixed IP.
3. Add regression tests for:
   - no fixed runtime IP in code paths
   - accepted-entry gating
   - 202 queue semantics for long-running routes
   - worker heartbeat reporting
   - progress UI on character detail
4. Write final repair reports under `docs/phase_reports/` and `docs/verification/`.

## Done when
- docs match the repaired runtime
- targeted tests cover the repaired flow
- verification reports are written
