# Phase 18 verification

## Scope verified

- `POST /api/v1/exports/characters/{character_public_id}/reconstruction` high-detail reconstruction path
- Structured reconstruction payload with truthful detail level and strategy
- Riggable base GLB availability after reconstruction
- Optional detail-prep artifact generation and retrieval
- Truthful Outputs UI reporting for the current reconstruction level
- Required lint and type-check gates

## Commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_reconstruction_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/reconstruction-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Files changed in the phase

- `PLANS.md`
- `README.md`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/schemas/exports.py`
- `apps/api/app/services/exports.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/services/reconstruction.py`
- `apps/api/tests/test_reconstruction_api.py`
- `apps/web/app/globals.css`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/reconstruction-status/ReconstructionStatus.tsx`
- `apps/web/tests/e2e/character-creation.spec.ts`
- `apps/web/tests/unit/reconstruction-status.test.tsx`
- `docs/architecture/character_outputs.md`
- `docs/architecture/high_detail_3d_path.md`
- `docs/phase_reports/phase_18.md`
- `docs/verification/phase_18_verify.md`

## Results

- PASS: the targeted backend test created a character from a six-image capture set, ran the reconstruction route, verified the structured response reported `riggable-base-plus-detail-prep` and `smplx-stage1-plus-colmap-prep`, fetched both the preview GLB and `detail-prep.json`, and confirmed the detail-prep storage object, completed reconstruction job, and reconstruction history rows were written.
- PASS: the targeted unit test proved the high-detail control posts to the reconstruction route and refreshes the character detail page after a successful response.
- PASS: the targeted Playwright flow created a character from the standard minimal sample set, generated a preview GLB, ran the high-detail path, and verified the Outputs section truthfully reported `riggable-base-only`, `smplx-stage1-only`, `Detail-prep artifact: not-ready`, and `Reconstruction job: completed`, with the new history entries surviving a full page reload.
- PASS: `make lint` and `make typecheck` completed successfully from the final Phase 18 tree.

## PASS/FAIL decision

PASS

## Remaining risks

- The current detail-prep artifact is a structured contract for later refinement work, not a claim that Phase 18 already reconstructs a finished detail mesh.
- The automatic gate for detail prep is intentionally coarse and should be tightened when later phases add real COLMAP-backed geometry work.
