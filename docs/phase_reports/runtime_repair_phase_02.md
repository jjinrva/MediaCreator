# Runtime Repair Phase 02

## Status

Implemented. Paired verification not yet run in this report.

## Goal

Keep upload/QC synchronous and truthful, make photoset acceptance explicit, and ensure base character creation uses accepted images only.

## Changes made

- updated [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py) to:
  - treat `pass` and `warn` as accepted for character use
  - expose `accepted_entry_count`
  - expose `rejected_entry_count`
  - expose per-entry `accepted_for_character_use`
- updated [photosets.py](/opt/MediaCreator/apps/api/app/schemas/photosets.py) so the API schema matches the new accepted/rejected payload contract
- updated [characters.py](/opt/MediaCreator/apps/api/app/services/characters.py) so:
  - only accepted entries flow into character creation
  - zero accepted entries raise a clear error
  - character detail payloads only surface accepted references
- inspected [characters.py](/opt/MediaCreator/apps/api/app/api/routes/characters.py) and kept the existing `400` mapping because it already translates the accepted-entry failure path truthfully
- updated [CharacterImportIngest.tsx](/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx) to show:
  - a visible three-step ingest flow
  - accepted and rejected counts
  - per-image accepted vs rejected state
  - clear accepted/rejected meaning text
  - the stronger `Build base character` CTA
  - the backend error detail when character creation is blocked
- updated related API, unit, and Playwright tests to lock the accepted-only behavior

## Result

- photoset payloads now distinguish accepted vs rejected entries explicitly
- rejected QC entries remain visible but do not flow into base character creation
- zero accepted entries are blocked with a clear `400`
- persisted QC results remain reloadable and the ingest UI explains what the counts mean

## Pre-verification evidence

- `cd /opt/MediaCreator/apps/api && .venv/bin/python -m pytest tests/test_photosets_api.py tests/test_characters_api.py` passed
- `cd /opt/MediaCreator/apps/web && ../../infra/bin/pnpm exec vitest run tests/unit/character-import.test.tsx` passed
