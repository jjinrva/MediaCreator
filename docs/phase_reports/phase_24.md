# Phase 24 report

## Status

PASS

## What changed

- Added the controlled video render service so the app now creates `character-motion-video` assets with explicit character and motion lineage, queues one render job, and registers one persisted MP4 output.
- Added the Blender render script at `workflows/blender/render_actions.py` so the first video path renders a real rig-driven clip in background mode instead of substituting AI video generation.
- Added the `/api/v1/video` API surface and the `/studio/video` route with a truthful HTML video player, download link, job state, and render history.
- Added focused backend, unit, and Playwright coverage that renders a short jump clip, verifies the output file exists, checks the lineage/history data, and confirms the UI can replay the clip after reload.
- Documented the controlled video contract and updated the root README with the new API and UI entrypoints.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_video_render_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/video-render-panel.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/video-render.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_video_render_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/video-render-panel.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/video-render.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- The scene is intentionally minimal and does not yet claim environment staging, cinematic cameras, or advanced lighting.
- The current render path reuses the proxy rig/mesh rather than claiming a refined final-body video path.
- Facial values are carried through the job contract, but Phase 24 does not claim full corrective facial animation yet.

## Next phase may start

Yes. Phase 24 verification passed, so Phase 25 may start.
