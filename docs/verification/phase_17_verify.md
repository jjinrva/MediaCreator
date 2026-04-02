# Phase 17 verification

## Scope verified

- `POST /api/v1/exports/characters/{character_public_id}/preview` Blender export path
- Real preview GLB file creation and `GET /api/v1/exports/characters/{character_public_id}/preview.glb` retrieval
- Truthful preview/export status rendering on the character detail route
- Job metadata and history writes for `job.completed` and `export.preview_generated`
- Required lint and type-check gates

## Commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_blender_export_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/glb-preview.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Files changed in the phase

- `PLANS.md`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/services/blender_runtime.py`
- `apps/api/app/services/exports.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/pyproject.toml`
- `apps/api/tests/test_blender_export_api.py`
- `apps/web/app/globals.css`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/glb-preview/GlbPreview.tsx`
- `apps/web/tests/e2e/character-creation.spec.ts`
- `apps/web/tests/unit/glb-preview.test.tsx`
- `apps/worker/pyproject.toml`
- `docs/phase_reports/phase_17.md`
- `docs/verification/phase_17_verify.md`
- `scripts/blender/rigify_proxy_export.py`
- `workflows/blender/rigify_proxy_export_v1.json`

## Results

- PASS: the targeted backend test created a character from a real photoset, ran the Blender preview export route, confirmed the returned job status was `completed`, fetched the generated GLB successfully, verified the storage path exists on disk, and confirmed `job.completed` plus `export.preview_generated` history records were written.
- PASS: the targeted unit test proved the `GlbPreview` control posts to the preview-export API and refreshes the route after a successful Blender job response.
- PASS: the targeted Playwright flow created a character, generated a preview GLB from the Outputs section, verified the viewer rendered, confirmed the UI showed `Preview GLB: available` and `Export job: completed`, and verified the new history entries survived a full page reload.
- PASS: `make lint` and `make typecheck` completed successfully from the final Phase 17 tree.

## PASS/FAIL decision

PASS

## Remaining risks

- The current export path proves the baseline Rigify-to-GLB preview loop, not the later high-detail reconstruction path.
- The browser verification covers the truthful preview/export states on a single happy path; broader retry and failure UX remains later work.
