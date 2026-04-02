# Phase 10 report

## Status

PASS

## What changed

- Added the FastAPI photoset upload route at `POST /api/v1/photosets`, plus reload and artifact routes under `/api/v1/photosets/{photoset_public_id}`.
- Added the `photo_prep` service to store original uploads, normalize them with Pillow, generate thumbnails, compute QC metrics, and persist the resulting metadata rows.
- Added the new `photoset_entries` table and model so each uploaded image has durable QC state plus explicit links to its original, normalized, and thumbnail storage objects.
- Added MediaPipe face and pose landmarker execution using the official task bundles, cached into the scratch storage root on first use.
- Added OpenCV blur and exposure heuristics plus a stable `pass`/`warn`/`fail` decision with visible reasons and framing labels.
- Updated `/studio/characters/new` so the same route now uploads to FastAPI, reloads stored QC results by `?photoset=` query param, and shows persisted thumbnail/status data after refresh.
- Updated Playwright to launch the API server for web tests and run `alembic upgrade head` before the browser suite so the Phase 10 tables exist in the live API database.
- Updated the environment contract with `NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL` and documented the new upload/QC API behavior in `README.md`.
- Fixed follow-up verification issues before final PASS:
  - removed the DB-dependency wrapper in the photoset route so test overrides hit the migrated test database instead of the default dev database
  - made the Playwright API server run migrations before `uvicorn` so browser upload tests exercise the real Phase 10 schema
  - resolved strict lint/type-check issues from long lines and untyped `mediapipe` imports

## Exact commands run

- `/opt/MediaCreator/apps/api/.venv/bin/pip install 'pillow<12' 'numpy<3' 'opencv-python-headless<5' 'mediapipe<1'`
- `cd /opt/MediaCreator/apps/api && .venv/bin/pip install -e '.[dev]'`
- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_photosets_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-ingest.spec.ts tests/e2e/character-upload-qc.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Tests that passed

- `cd /opt/MediaCreator/apps/api && .venv/bin/pytest tests/test_photosets_api.py -q`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/character-import.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/character-ingest.spec.ts tests/e2e/character-upload-qc.spec.ts`
- `make lint`
- `make typecheck`
- `make test-api`
- `make test-web`

## Remaining risks

- The current QC stack downloads MediaPipe task bundles on first use, so the first upload still depends on outbound network access if the scratch cache is empty.
- The upload flow currently reloads a complete photoset by URL query param; per-image replacement on an already persisted photoset still needs a later mutation path.
- The QC heuristics are intentionally lightweight in this phase and will need tuning as later phases bring in stricter body/face preparation requirements.

## Next phase may start

Yes. Phase 10 verification passed, so Phase 11 may start.
