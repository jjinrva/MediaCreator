# Phase
`phase_04_base_character_creation_and_saved_3d_output`

## Scope
Saved character creation from accepted assets only, truthful saved-GLB queueing, and detail-page status that stays artifact-backed.

## Files changed
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/services/characters.py`
- `apps/api/app/services/blender_runtime.py`
- `apps/api/app/services/reconstruction.py`
- `apps/api/app/services/exports.py`
- `apps/api/app/schemas/characters.py`
- `apps/api/tests/test_character_creation_from_classified_photoset.py`
- `apps/api/tests/test_saved_3d_output_contract.py`
- `tests/api/test_character_creation_from_classified_photoset.py`
- `tests/api/test_saved_3d_output_contract.py`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/glb-preview/GlbPreview.tsx`
- `apps/web/tests/e2e/character_detail_saved_glb.spec.ts`
- `apps/web/playwright.config.js`

## Implementation summary
- Kept character creation acceptance-gated and tightened lineage persistence so the saved character history now records:
  - accepted source entry IDs
  - separated body-qualified entry/photo IDs
  - separated LoRA-qualified entry/photo IDs
- Allowed duplicate human-facing labels to continue flowing through saved character creation without collapsing distinct character IDs.
- Changed Blender preview export inputs to use accepted sources only and to prefer persisted body-derivative assets for body-qualified entries.
- Changed reconstruction assessment to use body-qualified count for refinement truth:
  - `>= 3` body-qualified images => `riggable-base-plus-detail-prep`
  - `< 3` body-qualified images => `riggable-base-only`
- Added `body_qualified_entry_count` to the queued reconstruction payload so job history and output truth no longer infer readiness from total accepted count.
- Updated reconstruction/detail messaging so the API explains when refinement is unavailable because capture breadth is below the body-qualified threshold.
- Extended the character detail schema so accepted references keep their bucket and reason data visible on the saved character route.
- Updated the detail page and GLB viewer copy to stay truthful:
  - saved-output wording instead of phase-specific claims
  - visible full-body framing label
  - artifact-backed preview detail only when the saved GLB exists
- Isolated Playwright onto dedicated test ports so the phase verification no longer reuses whatever live dev stack is already running on `3000/8010`.

## Verification hooks added
- `apps/api/tests/test_character_creation_from_classified_photoset.py`
- `apps/api/tests/test_saved_3d_output_contract.py`
- root-level wrappers under `tests/api/` for the pack’s exact pytest paths
- `apps/web/tests/e2e/character_detail_saved_glb.spec.ts`

## Known limitations
- The real sample set used by the browser test still auto-classified as a minimal accepted set, so the Phase 04 browser check focuses on truthful queue-to-artifact behavior rather than proving a high-detail body-prep outcome.
- Phase 04 does not yet create a saved LoRA artifact or proof image. That remains Phase 05 scope.

## Status
PASS
