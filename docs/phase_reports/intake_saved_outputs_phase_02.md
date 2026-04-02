# Phase
`phase_02_frontend_intake_truth_label_and_thumbnail_preview`

## Scope
Operator-facing intake UI changes for required labels, truthful upload/server progress, persisted bucket summaries, and thumbnail inspection.

## Files changed
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- `apps/web/app/globals.css`
- `apps/web/lib/jobProgress.ts`
- `apps/web/playwright.config.js`
- `apps/web/tests/unit/CharacterImportIngest.test.tsx`
- `apps/web/tests/e2e/character_intake_truth.spec.ts`
- `apps/web/tests/e2e/character_thumbnail_preview.spec.ts`

## Implementation summary
- Added a required character-label field at the top of the intake form and kept duplicate labels allowed.
- Switched upload submission to `XMLHttpRequest` so browser transfer progress is visible during the actual upload.
- Polled the persisted ingest job and saved photoset so the UI shows backend-reported stage names, processed counts, and bucket totals instead of a vague hanging state.
- Rendered explicit bucket summary cards for:
  - `lora_only`
  - `body_only`
  - `both`
  - `rejected`
- Kept character creation gated until ingest is complete and at least one accepted image exists.
- Made staged and persisted thumbnails clickable, opening an accessible enlarged preview dialog with backend bucket/reason/QC details and keyboard escape close handling.
- Normalized job bucket-count typing in the UI layer so the progress contract stays strict under `tsc`.
- Enabled Playwright to reuse the already-running local stack during deterministic UI proof.

## Verification hooks added
- `apps/web/tests/unit/CharacterImportIngest.test.tsx`
- `apps/web/tests/e2e/character_intake_truth.spec.ts`
- `apps/web/tests/e2e/character_thumbnail_preview.spec.ts`

## Known limitations
- This phase only covers the intake screen and preview flow. Saved derivative lineage, 3D output truth, and LoRA output truth remain later phases.
- The preview dialog is implemented with existing app primitives and custom accessible markup; no new dialog library was introduced.

## Status
PASS
