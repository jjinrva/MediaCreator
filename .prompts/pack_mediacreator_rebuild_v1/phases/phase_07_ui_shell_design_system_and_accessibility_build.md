# Phase 07 build — UI shell, design system, tooltips, and accessibility baseline

## Goal

Create the MediaCreator shell, navigation, typography, buttons, cards, tabs, tooltips, and the permanent info-icon pattern for every input control.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Next.js App Router
- Radix Tooltip
- Radix Slider
- Playwright

### Source IDs to use for this phase
S01, S04, S05, S06



## Files and directories this phase is allowed to create or modify first

- apps/web/app
- apps/web/components/ui
- apps/web/tests/unit
- apps/web/tests/e2e

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create the main app shell and `/studio` landing route. Use a clean, professional layout with left navigation, top status strip, and content area. Do not show fake counts or fake data.

### Step 2
Create reusable UI primitives now: `InfoTooltip`, `NumericSliderField`, `EmptyState`, `PageHeader`, `SectionCard`, `KeyValueList`, `HistoryList`, and `FileTile`. Put them in a shared UI folder so later phases do not duplicate implementations.

### Step 3
Create the permanent rule that every slider or textbox gets a small info icon that reveals help on hover or focus. The tooltip content should come from the field metadata, not inline duplicated strings wherever possible.

### Step 4
Add a simple theme system and keyboard-accessible tabs/panels. Use semantic headings, labels, and button names so Playwright can target them with user-facing locators.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_07.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- Studio shell
- shared UI primitives
- tooltip rule
- basic route smoke tests

## What Codex must not do in this phase


- Do not create parallel implementations of the same concept.
- Do not add auth or multi-user logic in this phase unless the phase explicitly says to create future-ready fields only.
- Do not seed runtime screens with demo/sample data.
- Do not change the chosen stack.
- Do not continue to the next phase until this phase passes verify.


## Exit condition for the build phase

The build phase may stop only when:
1. the phase deliverables exist,
2. the changed code is coherent,
3. the paired verify file has enough hooks to test the phase honestly,
4. `docs/phase_reports/phase_07.md` is updated with exact commands and results.
