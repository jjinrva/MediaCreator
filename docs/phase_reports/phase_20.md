# Phase 20 report

## Status

PASS

## What changed

- Added the LoRA dataset curation service so the app now builds a versioned dataset folder from the character’s accepted prepared images and writes a manifest with source lineage.
- Added the explicit prompt-handle contract so `@character` expansion is visible, versioned, and auditable instead of being hidden in a later generation phase.
- Added the LoRA dataset API with status/load, build, and manifest download routes.
- Added a dedicated LoRA Dataset section to the character detail page with a build button, visible tags, prompt handle, and expansion string.
- Added focused backend, unit, and Playwright coverage for dataset file creation, manifest correctness, visible prompt expansion, and dataset history writes.
- Documented the dataset layout and prompt-handle contract in architecture notes and the root README.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_lora_dataset_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/lora-dataset-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_lora_dataset_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/lora-dataset-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- Phase 20 prepares the dataset and prompt contract only; it does not claim local LoRA training is running yet.
- The current caption strategy is explicit and stable, but still simple. Later phases may enrich tags while keeping the contract versioned.
- Dataset creation currently requires a NAS-backed LoRA storage root. That is intentional and truthfully enforced.

## Next phase may start

Yes. Phase 20 verification passed, so Phase 21 may start.
