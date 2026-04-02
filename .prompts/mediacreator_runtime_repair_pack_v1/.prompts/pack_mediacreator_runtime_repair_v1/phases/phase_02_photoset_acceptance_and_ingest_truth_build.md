# Phase 02 build — photoset acceptance and ingest truth

## Goal
Make upload/QC truthful and make character creation use accepted images only.

## Exact decisions
- Keep upload/QC synchronous so the user receives immediate QC results.
- Treat `qc_status in {"pass","warn"}` as accepted.
- Treat `qc_status == "fail"` as rejected.
- Expose accepted and rejected counts in the photoset payload.
- Character creation must use accepted entries only.
- Character creation must fail clearly when accepted count is zero.
- The upload screen must show a visible stepper and accepted/rejected summary.

## Files to inspect and edit
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/schemas/photosets.py`
- `apps/api/app/services/characters.py`
- `apps/api/app/api/routes/characters.py`
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- related tests

## Exact steps
1. Extend the photoset payload to include:
   - `accepted_entry_count`
   - `rejected_entry_count`
   - per-entry `accepted_for_character_use`
2. Update character creation so only accepted entries flow into the base character.
3. Reject character creation with a clear 400 if zero accepted entries exist.
4. Update the ingest screen to display:
   - accepted count
   - rejected count
   - what accepted means
   - what rejected means
   - a stronger CTA label (use `Build base character`)
5. Keep the persisted QC results reloadable.

## Required code patterns
Use the accepted-entry filtering pattern in `CODE_EXAMPLES.md` section 2.

## Do not do
- do not use failed entries when creating a character
- do not make upload asynchronous in this pack
- do not hide rejected images; keep them visible with their reasons

## Done when
- the API returns accepted/rejected counts
- the upload page shows those counts
- zero accepted entries blocks character creation
- characters only reference accepted entries
