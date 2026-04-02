# Runtime Repair Phase 05

## Status

PASS

## Goal

Finish the runtime repair pack by aligning docs, test defaults, and regression coverage with the repaired host/origin strategy plus the truthful queued-job flow.

## Changes made

- updated [README.md](/opt/MediaCreator/README.md) to explain the repaired runtime contract:
  - bind host vs browser host
  - synchronous upload/QC
  - queued preview/reconstruction/LoRA/video jobs
  - `/api/v1/jobs/{job_public_id}` progress polling
  - `/api/v1/system/status` worker heartbeat relevance
- updated [operator_runbook.md](/opt/MediaCreator/docs/handoff/operator_runbook.md) with the actual operator flow for immediate ingest vs queued background jobs and the worker-heartbeat troubleshooting path
- normalized stale machine-specific host examples in:
  - [runtime_repair_verify_phase_01.md](/opt/MediaCreator/docs/verification/runtime_repair_verify_phase_01.md)
  - [runtime_repair_verify_phase_02.md](/opt/MediaCreator/docs/verification/runtime_repair_verify_phase_02.md)
- updated [playwright.config.js](/opt/MediaCreator/apps/web/playwright.config.js) so the default browser-side host assumption is `localhost` and still remains env-overridable
- updated Playwright helpers/specs to derive API base from `MEDIACREATOR_PLAYWRIGHT_HOST` instead of hardcoding one IP:
  - [worker.ts](/opt/MediaCreator/apps/web/tests/e2e/helpers/worker.ts)
  - [video-render.spec.ts](/opt/MediaCreator/apps/web/tests/e2e/video-render.spec.ts)
  - [settings-diagnostics.spec.ts](/opt/MediaCreator/apps/web/tests/e2e/settings-diagnostics.spec.ts)
  - [generation-workspace.spec.ts](/opt/MediaCreator/apps/web/tests/e2e/generation-workspace.spec.ts)
  - [motion-library.spec.ts](/opt/MediaCreator/apps/web/tests/e2e/motion-library.spec.ts)
- updated those browser specs to use the stable accepted sample `male_head_front.png` so accepted-entry gating remains truthful under the repaired QC contract
- extended [runtime-api-base.test.ts](/opt/MediaCreator/apps/web/tests/unit/runtime-api-base.test.ts) with a regression test that proves the browser API base follows the active hostname instead of any fixed LAN IP
- repaired strict backend test typing in:
  - [test_photosets_api.py](/opt/MediaCreator/apps/api/tests/test_photosets_api.py)
  - [test_characters_api.py](/opt/MediaCreator/apps/api/tests/test_characters_api.py)
  - [test_jobs_service.py](/opt/MediaCreator/apps/api/tests/test_jobs_service.py)
  so the final backend `mypy` gate passes under the current strict config
- updated [JobProgressCard.tsx](/opt/MediaCreator/apps/web/components/jobs/JobProgressCard.tsx) so its polling effect depends on explicit job primitives instead of a closed-over object, which clears the final `react-hooks/exhaustive-deps` lint gate without changing runtime behavior
- Phase 04 verification artifacts are now in place under:
  - [runtime_repair_phase_04.md](/opt/MediaCreator/docs/phase_reports/runtime_repair_phase_04.md)
  - [runtime_repair_verify_phase_04.md](/opt/MediaCreator/docs/verification/runtime_repair_verify_phase_04.md)

## Result

- runtime docs now describe the repaired behavior instead of the old inline-job assumption
- the Playwright/browser-side test harness no longer assumes one fixed LAN IP
- regression coverage now protects host derivation, accepted-entry gating, and the repaired queued-job browser flow
- stale `10.0.0.102` examples are removed from runtime docs and runtime-oriented verification docs
- paired verification passed after repairing one strict-typing regression and one web hook-lint regression discovered during the final gates

## Pre-verification evidence

- `rg -n "10\\.0\\.0\\.102" /opt/MediaCreator/README.md /opt/MediaCreator/docs/handoff /opt/MediaCreator/docs/verification /opt/MediaCreator/apps/web /opt/MediaCreator/apps/api/tests || true` returned no matches
- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH /opt/MediaCreator/infra/bin/pnpm exec vitest run tests/unit/runtime-api-base.test.ts` passed with `5` tests
- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH PLAYWRIGHT_BROWSERS_PATH=/opt/MediaCreator/infra/playwright /opt/MediaCreator/infra/bin/pnpm exec playwright test tests/e2e/settings-diagnostics.spec.ts tests/e2e/generation-workspace.spec.ts tests/e2e/motion-library.spec.ts` passed with `3` browser tests
- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH PLAYWRIGHT_BROWSERS_PATH=/opt/MediaCreator/infra/playwright /opt/MediaCreator/infra/bin/pnpm exec playwright test tests/e2e/character-creation.spec.ts tests/e2e/video-render.spec.ts` passed with `2` browser tests

## Final verification outcome

- backend lint passed for API and worker
- backend typecheck passed for API (`100` source files) and worker (`2` source files)
- targeted backend runtime tests passed: `10` tests
- web lint passed
- web typecheck passed
- targeted web unit tests passed: `8` files, `16` tests
- targeted Playwright regressions passed: `5` tests
