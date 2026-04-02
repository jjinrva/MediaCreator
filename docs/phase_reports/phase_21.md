# Phase 21 report

## Status

PASS

## What changed

- Added the NAS-backed `models_registry` table and ORM model for character-scoped LoRA records.
- Added the Phase 21 LoRA training service so the API now reports truthful AI Toolkit readiness, tracks `working/current/failed/archived` registry states, and resolves the active LoRA artifact for generation.
- Added `/api/v1/lora/characters/{character_public_id}` GET/POST routes plus response schemas for training readiness, registry state, and active-model reporting.
- Added the LoRA Training section to the character detail page with a disabled local-training action when AI Toolkit is unavailable.
- Added focused backend, unit, and Playwright coverage for truthful disabled capability reporting, registry state handling, and active LoRA resolution.
- Documented the model-registry and activation contract in architecture notes and the root README.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_lora_training_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/lora-training-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_lora_training_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/lora-training-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- AI Toolkit is not installed in this environment, so the real trainer execution path remains truthfully unavailable and was not exercised end-to-end here.
- Phase 21 resolves the active LoRA artifact for generation, but the actual ComfyUI graph injection still belongs to later phases.
- The registry is character-scoped today; later phases may add more specific style/variant scoping while preserving one-current semantics.

## Next phase may start

Yes. Phase 21 verification passed, so Phase 22 may start.
