# Phase 08 report

## Status

PASS

## What changed

- Rendered a real Phase 08 capture-board asset set with Blender 4.5.4 LTS into `docs/capture_guides/assets`, covering male and female full-body front, left, right, back, three-quarter, plus front/left/right head views.
- Added the `/studio/capture-guide` route with concrete onboarding instructions for shot count, camera distance, overlap, lighting, clothing, backgrounds to avoid, and an explicit warning that later high-detail 3D phases need significantly more photos than LoRA.
- Added a local asset-serving route at `/studio/capture-guide/assets/[assetName]` so the page renders the tracked guide PNG files directly from the repository instead of copying them into a separate runtime sample area.
- Added a shared `StudioFrame` wrapper so the Phase 07 shell and the new Phase 08 route use the same truthful studio navigation.
- Wrote the paired markdown guide at `docs/capture_guides/capture_guide.md` and updated `README.md` with the new route and the Blender re-render command.
- Added focused unit and Playwright coverage for the new route and expanded the studio navigation smoke test.
- Fixed follow-up verification issues before final PASS:
  - added the explicit `React` import required by the capture-guide server page test
  - tightened the Playwright image locator to avoid an ambiguous substring match across the male and female front-board images

## Exact commands run

- `/opt/blender-4.5-lts/blender --version | head -n 2`
- `chmod +x /opt/MediaCreator/scripts/blender/render_capture_guides.sh && /opt/MediaCreator/scripts/blender/render_capture_guides.sh`
- `test -f /opt/MediaCreator/docs/capture_guides/capture_guide.md && find /opt/MediaCreator/docs/capture_guides/assets -maxdepth 1 -type f -name '*.png' | sort`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/ui-primitives.test.tsx tests/unit/capture-guide.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/studio.spec.ts tests/e2e/capture-guide.spec.ts`
- `make lint`
- `make typecheck`
- `make test-web`

## Tests that passed

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/ui-primitives.test.tsx tests/unit/capture-guide.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/studio.spec.ts tests/e2e/capture-guide.spec.ts`
- `make lint`
- `make typecheck`
- `make test-web`

## Remaining risks

- The capture guidance is static onboarding content in this phase; the upload/QC pipeline that enforces these expectations arrives in later phases.
- The Blender board assets are intentionally generic mannequin references, not production character assets or runtime sample library content.
- The route serves only the tracked Phase 08 asset filenames; if later phases rename or replace those files, the allowlist in the asset route must be updated at the same time.

## Next phase may start

Yes. Phase 08 verification passed, so Phase 09 may start.
