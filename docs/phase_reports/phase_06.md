# Phase 06 report

## Status

PASS

## What changed

- Added a ComfyUI capability service that reports `unavailable`, `partially-configured`, or `ready` based on the configured base URL, workflow files, NAS-backed model roots, and detected checkpoint/VAE files.
- Added `GET /api/v1/system/status` so the API can report truthful generation capability without pretending that image generation is already runnable.
- Extended the fixed storage contract with NAS-backed embeddings and VAE roots alongside checkpoints and LoRAs.
- Added the versioned workflow folder contract under `workflows/comfyui/` with stable placeholder JSON files and a README documenting their names and purpose.
- Updated the landing page and docs so MediaCreator now says generation remains unavailable until ComfyUI, workflow JSON, and NAS model roots are actually detected.
- Added focused backend tests for absent ComfyUI, configured workflow/model roots, and partial capability status when the service is unreachable.
- Fixed follow-up verification issues before final PASS:
  - enabled attribute-based validation for the nested generation schema
  - handled the optional ComfyUI base URL without tripping mypy
  - normalized import ordering in the new API files with Ruff

## Exact commands run

- `apps/api/.venv/bin/pytest apps/api/tests/test_generation_provider.py apps/api/tests/test_storage_service.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts`
- `find /opt/MediaCreator/workflows/comfyui -maxdepth 1 -type f | sort`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`
- `cd /opt/MediaCreator/apps/api && .venv/bin/ruff check app tests --fix`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Tests that passed

- `apps/api/.venv/bin/pytest apps/api/tests/test_generation_provider.py apps/api/tests/test_storage_service.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts`
- `find /opt/MediaCreator/workflows/comfyui -maxdepth 1 -type f | sort`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Remaining risks

- Phase 06 only validates capability; it does not enqueue or run a real ComfyUI workflow yet.
- `ready` status still depends on an external local ComfyUI service actually responding at the configured base URL.
- The workflow JSON files are stable placeholders today and will need real node graphs in later phases.

## Next phase may start

Yes. Phase 06 verification passed, so Phase 07 may start.
