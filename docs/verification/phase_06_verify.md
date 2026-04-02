# Phase 06 verification

## Scope verified

- Truthful ComfyUI capability reporting through `GET /api/v1/system/status`
- Unavailable status when ComfyUI is absent
- Workflow and NAS model-root validation when local paths are configured
- NAS-backed storage roots for checkpoints, LoRAs, embeddings, and VAEs
- Stable workflow-folder contract under `workflows/comfyui/`
- Truthful landing-page copy for generation readiness
- Required regression gates across API, web, lint, and type-checking

## Commands run

- `apps/api/.venv/bin/pytest apps/api/tests/test_generation_provider.py apps/api/tests/test_storage_service.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts`
- `find /opt/MediaCreator/workflows/comfyui -maxdepth 1 -type f | sort`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Files changed in the phase

- `.env.example`
- `README.md`
- `PLANS.md`
- `docs/architecture/generation_capability.md`
- `docs/architecture/local_runtime.md`
- `docs/architecture/storage_layout.md`
- `docs/phase_reports/phase_06.md`
- `docs/verification/phase_06_verify.md`
- `apps/api/app/api/router.py`
- `apps/api/app/api/routes/system.py`
- `apps/api/app/schemas/system.py`
- `apps/api/app/services/generation_provider.py`
- `apps/api/app/services/storage_service.py`
- `apps/api/tests/test_generation_provider.py`
- `apps/api/tests/test_storage_service.py`
- `apps/web/app/layout.tsx`
- `apps/web/app/page.tsx`
- `apps/web/tests/e2e/home.spec.ts`
- `apps/web/tests/unit/home.test.tsx`
- `workflows/comfyui/README.md`
- `workflows/comfyui/character_refine_img2img_v1.json`
- `workflows/comfyui/text_to_image_v1.json`

## Results

- PASS: the system-status route reported `unavailable` when the ComfyUI base URL was absent and did not claim `ready`.
- PASS: with temporary workflow/model paths configured and the ComfyUI ping mocked as reachable, the system-status route reported `ready` and exposed NAS-backed checkpoint, LoRA, embeddings, and VAE roots.
- PASS: with the same paths configured but the service ping failing, the capability service reported `partially-configured` with `comfyui_service_unreachable`.
- PASS: the tracked workflow folder now contains `README.md`, `text_to_image_v1.json`, and `character_refine_img2img_v1.json`.
- PASS: the updated home-page unit test and Playwright spec showed truthful generation-readiness copy.
- PASS: `make test-api`, `make test-web`, `make lint`, and `make typecheck` all completed successfully from the final tree.

## PASS/FAIL decision

PASS

## Remaining risks

- The route reports capability only; there is still no real ComfyUI job submission or output validation.
- Real target environments must provide a responding ComfyUI service plus actual checkpoint and VAE files before the capability route can return `ready`.
- Workflow filenames are now fixed, but the placeholder JSON content still needs real graphs in later phases.
