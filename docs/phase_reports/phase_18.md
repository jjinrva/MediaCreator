# Phase 18 report

## Status

PASS

## What changed

- Added the high-detail reconstruction service contract so the app now chooses one truthful two-stage path: a riggable SMPL-X-family base first, then an optional COLMAP-backed detail-prep stage when the capture set qualifies.
- Added the `high-detail-reconstruction` job payload and worker execution path so reconstruction writes durable job state, storage-object outputs, and history records.
- Extended the exports API contract with reconstruction status, strategy, riggable-base availability, and optional detail-prep artifact exposure, plus a `POST /api/v1/exports/characters/{character_public_id}/reconstruction` trigger route.
- Added the optional `detail-prep.json` artifact route and kept the riggable base tied to the real Blender GLB output instead of inventing a second uncontrolled mesh path.
- Updated the character detail page with a dedicated high-detail control and truthful Outputs rows for detail level, strategy, base-asset status, detail-prep status, and reconstruction job status.
- Documented the two-stage high-detail path, the current coarse capture gate, and the real capture requirements in architecture docs and the root README.

## Exact commands run

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_reconstruction_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/reconstruction-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_reconstruction_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/reconstruction-status.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-creation.spec.ts`
- `make lint`
- `make typecheck`

## Remaining risks

- Phase 18 still stops at a riggable base plus an optional detail-prep manifest; it does not claim a finished refined mesh or texture-projected reconstruction yet.
- The current capture gate for writing the detail-prep artifact is intentionally coarse and count-based. Manual review for overlap, lighting, and subject consistency is still required.
- The riggable base artifact currently reuses the Blender preview GLB path; later phases may split preview and reconstruction exports more explicitly if the pipeline needs it.

## Next phase may start

Yes. Phase 18 verification passed, so Phase 19 may start.
