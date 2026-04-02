# Phase 08 verification

## Scope verified

- The `/studio/capture-guide` route renders with truthful studio navigation and concrete onboarding copy.
- The paired markdown guide exists at `docs/capture_guides/capture_guide.md`.
- The rendered Blender asset set exists under `docs/capture_guides/assets` and the web route serves those PNG files through `/studio/capture-guide/assets/[assetName]`.
- The page includes specific shot-count, distance, overlap, lighting, clothing, background, and high-detail-3D guidance instead of placeholder text.
- Web linting, type-checking, and the broader web regression target all pass from the final tree.

## Commands run

- `test -f /opt/MediaCreator/docs/capture_guides/capture_guide.md && find /opt/MediaCreator/docs/capture_guides/assets -maxdepth 1 -type f -name '*.png' | sort`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/ui-primitives.test.tsx tests/unit/capture-guide.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/studio.spec.ts tests/e2e/capture-guide.spec.ts`
- `make lint`
- `make typecheck`
- `make test-web`

## Files changed in the phase

- `README.md`
- `PLANS.md`
- `docs/capture_guides/capture_guide.md`
- `docs/capture_guides/assets/*.png` (16 rendered files)
- `docs/phase_reports/phase_08.md`
- `docs/verification/phase_08_verify.md`
- `scripts/blender/render_capture_guides.py`
- `scripts/blender/render_capture_guides.sh`
- `apps/web/app/globals.css`
- `apps/web/app/studio/page.tsx`
- `apps/web/app/studio/capture-guide/content.ts`
- `apps/web/app/studio/capture-guide/page.tsx`
- `apps/web/app/studio/capture-guide/assets/[assetName]/route.ts`
- `apps/web/components/ui/StudioFrame.tsx`
- `apps/web/tests/e2e/capture-guide.spec.ts`
- `apps/web/tests/e2e/studio.spec.ts`
- `apps/web/tests/unit/capture-guide.test.tsx`

## Results

- PASS: the markdown guide exists and 16 rendered PNG assets are present in `docs/capture_guides/assets`.
- PASS: the focused unit tests proved the new route renders concrete instructions and references the full rendered asset set.
- PASS: the focused Playwright checks proved `/studio/capture-guide` renders, the capture-guide nav item is the active page, and `/studio/capture-guide/assets/male_body_front.png` returns `image/png`.
- PASS: the route copy is concrete and actionable, including exact photo-count ranges, distance ranges, overlap, lighting, wardrobe, backgrounds to avoid, and the stronger photo requirement for later high-detail 3D work.
- PASS: `make lint`, `make typecheck`, and `make test-web` all completed successfully from the final tree.

## PASS/FAIL decision

PASS

## Remaining risks

- Phase 08 proves the onboarding content and tracked assets only; upload-time photo QC enforcement is still deferred to later phases.
- The asset route intentionally serves only the known Phase 08 guide files, so new filenames require a matching allowlist update.
- The guidance is written for a neutral standing capture; specialized wardrobe, hair, or reflective-material cases may still need more photos than the published minimums.
