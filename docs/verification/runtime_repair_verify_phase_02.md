# Runtime Repair Phase 02 Verification

## Status

PASS

## API gates

Command:

```bash
cd /opt/MediaCreator/apps/api
.venv/bin/python -m pytest tests/test_photosets_api.py tests/test_characters_api.py
```

Result:
- `3` tests passed

Verified by those tests:
- uploading a mixed photoset returns `accepted_entry_count`, `rejected_entry_count`, and per-entry `accepted_for_character_use`
- failed QC entries are flagged as rejected
- character creation returns `400` when accepted count is zero
- character creation with mixed `pass` / `warn` / `fail` entries links only accepted entries

## UI gates

Command:

```bash
cd /opt/MediaCreator/apps/web
PLAYWRIGHT_BROWSERS_PATH=/opt/MediaCreator/infra/playwright \
MEDIACREATOR_PLAYWRIGHT_HOST=<current-lan-host> \
MEDIACREATOR_PLAYWRIGHT_WEB_BASE_URL=http://<current-lan-host>:3000 \
MEDIACREATOR_PLAYWRIGHT_API_BASE_URL=http://<current-lan-host>:8010 \
../../infra/bin/pnpm exec playwright test \
  tests/e2e/character-upload-qc.spec.ts \
  tests/e2e/character-creation.spec.ts
```

Result:
- `2` tests passed

Verified by those tests:
- upload shows accepted and rejected counts
- the main CTA reads `Build base character`
- rejected items remain visible with reasons
- persisted QC results reload correctly from the URL photoset id
- a mixed accepted/rejected photoset can still build a base character from accepted entries only

## Test gates

Ingest unit test:

```bash
cd /opt/MediaCreator/apps/web
../../infra/bin/pnpm exec vitest run tests/unit/character-import.test.tsx
```

Result:
- `1` file passed
- `3` tests passed

Verified by that test:
- the ingest UI shows the accepted/rejected contract
- the CTA label is `Build base character`
- zero accepted entries disable character creation and keep rejected state visible

## Repair notes

- the first Playwright verify run failed because broad text locators matched both the summary text and the status badges
- repaired by scoping the assertions to the persisted status strip and thumbnail cards
- the first mixed-sample Playwright fixture also used images that both failed QC in the live runtime
- repaired by probing the capture-guide assets and switching to a stable mixed set:
  - accepted: `male_head_front.png`
  - rejected: `female_head_front.png`
- a final brittle rejected-reason string check was replaced with the actual UI contract: the rejected card must remain visible and show at least one reason item

## Conclusion

Phase 02 is verified complete:
- upload/QC remains synchronous
- accepted vs rejected state is explicit in the API and UI
- failed QC entries do not flow into character creation
- zero accepted entries are blocked clearly
