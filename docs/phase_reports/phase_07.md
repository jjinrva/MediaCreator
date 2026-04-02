# Phase 07 report

## Status

PASS

## What changed

- Added the permanent `/studio` shell route with left navigation, a top status strip, accessible tabs, and truthful empty-state content.
- Added the shared Phase 07 UI primitives under `apps/web/components/ui`: `InfoTooltip`, `NumericSliderField`, `EmptyState`, `PageHeader`, `SectionCard`, `KeyValueList`, `HistoryList`, and `FileTile`.
- Enforced the permanent input-help rule by placing an adjacent info tooltip trigger next to every visible slider and textbox in the Phase 07 shell.
- Added a simple `dawn`/`midnight` theme system using CSS variables on `html[data-theme]`.
- Updated the front door at `/` so it links into `/studio` and describes the new shell truthfully.
- Added focused unit coverage for the shared primitives and focused Playwright smoke coverage for both `/` and `/studio`.
- Fixed follow-up verification issues before final PASS:
  - added a `ResizeObserver` stub for Radix Slider in jsdom unit tests
  - exposed an explicit `navigation` landmark label for the studio nav
  - replaced the CSS `align-items: end` value with `flex-end` to avoid the postcss warning

## Exact commands run

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm install`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx tests/unit/ui-primitives.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts tests/e2e/studio.spec.ts`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Tests that passed

- `PATH="/opt/MediaCreator/infra/bin:$PATH" pnpm --dir /opt/MediaCreator/apps/web exec vitest run tests/unit/home.test.tsx tests/unit/ui-primitives.test.tsx`
- `PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm --dir /opt/MediaCreator/apps/web exec playwright test tests/e2e/home.spec.ts tests/e2e/studio.spec.ts`
- `make test-api`
- `make test-web`
- `make lint`
- `make typecheck`

## Remaining risks

- The shell is still scaffolding only; character editing, ingest, and generation workflows are not wired into the UI yet.
- The theme choice is session-local and intentionally does not persist into product state.
- Phase 07 proves the tooltip rule on the current shell controls, but later phases must keep using the same shared primitives instead of duplicating new input patterns.

## Next phase may start

Yes. Phase 07 verification passed, so Phase 08 may start.
