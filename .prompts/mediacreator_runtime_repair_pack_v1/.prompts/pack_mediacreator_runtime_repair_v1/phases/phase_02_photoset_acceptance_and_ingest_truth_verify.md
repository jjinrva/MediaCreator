# Phase 02 verify — photoset acceptance and ingest truth

## Verify with code and commands

### API gates
- upload a mixed photoset
- confirm payload contains accepted and rejected counts
- confirm failed entries are flagged as rejected
- attempt character creation with zero accepted entries and expect 400
- create a character with mixed pass/warn/fail entries and confirm only pass/warn entries are linked

### UI gates
- upload photos
- verify the page shows accepted and rejected counts
- verify the main CTA reads `Build base character`
- verify rejected items remain visible with reasons

### Test gates
- photoset API tests
- character creation API tests
- ingest unit tests
- ingest Playwright tests

## Phase fails if
- failed entries still flow into character creation
- the UI does not explain accepted vs rejected state
- the CTA remains ambiguous
