# Studio shell

## Purpose

Phase 07 establishes the permanent MediaCreator web shell before character, capture, and generation workflows arrive.

## Route structure

- `/`
  Truthful front door for the rebuild with a direct link into the studio shell.
- `/studio`
  Main shell route with left navigation, top status strip, accessible tabs, and empty-state content.

## Shared UI primitives

The shared UI layer now lives under `apps/web/components/ui/` and includes:

- `InfoTooltip`
- `NumericSliderField`
- `EmptyState`
- `PageHeader`
- `SectionCard`
- `KeyValueList`
- `HistoryList`
- `FileTile`

## Tooltip rule

- Every visible slider and textbox must have an adjacent info icon.
- Tooltip content comes from field metadata rather than duplicated inline strings whenever possible.
- Tooltip triggers expose user-facing names so Playwright and assistive tech can target them reliably.

## Accessibility baseline

- Tabs use `role="tablist"`, `role="tab"`, and `role="tabpanel"`.
- Navigation links and buttons use visible text or explicit accessible labels.
- Empty states stay truthful and do not fabricate records, counts, or job history.

## Theme system

- The shell supports `dawn` and `midnight` themes through CSS variables on `html[data-theme]`.
- The theme toggle changes shell presentation only. It does not write product data.
