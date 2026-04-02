# Phase 25 report

## Status

PASS

## What changed

- Added the standalone generation workspace so prompt staging now happens away from the 3D editing routes at `/studio/generate`.
- Added the prompt-expansion service and `POST /api/v1/generation/expand` so `@character` handles resolve into a visible full prompt recipe.
- Added generation-request storage so requests now persist the raw prompt, expanded prompt, workflow contract, provider status, and linked local/external LoRA references.
- Added registry-backed local LoRA selection in the workspace and an opt-in Civitai discovery/import path that writes imported external models into the internal registry before they can be used.
- Added focused backend, unit, and Playwright coverage for prompt expansion, request storage, local LoRA linkage, and reload behavior.
- Documented the generation workspace contract and updated the root README with the new API and UI entrypoints.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_generation_workspace_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/generation-workspace.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/generation-workspace.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_generation_workspace_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/generation-workspace.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/generation-workspace.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- Phase 25 stores truthful request metadata and model references, but it does not yet claim final image/video artifacts exist.
- The Civitai path is intentionally opt-in and was not enabled during verification, so import remains documented and guarded rather than exercised in the default environment.
- Local LoRA activation is verified at request-storage level, not via a final ComfyUI output artifact.

## Next phase may start

Yes. Phase 25 verification passed, so Phase 26 may start.
