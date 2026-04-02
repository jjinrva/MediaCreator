# Phase
`phase_04_base_character_creation_and_saved_3d_output`

## Scope verified
- character creation fails when all inputs are rejected
- duplicate labels still create distinct saved character IDs
- accepted source lineage persists with separated body and LoRA subsets
- the saved-GLB route returns queued job metadata instead of inline completion
- the saved GLB is reported as available only after a real file exists and a storage row is registered
- the detail page shows the queued/running job state before the GLB exists and still resolves the saved GLB after reload
- repo lint and typecheck pass after the Phase 04 changes

## Commands run
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_character_creation_from_classified_photoset.py`
- `cd /opt/MediaCreator && apps/api/.venv/bin/pytest -q tests/api/test_saved_3d_output_contract.py`
- `cd /opt/MediaCreator/apps/web && PATH="/opt/MediaCreator/infra/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="/opt/MediaCreator/infra/playwright" pnpm exec playwright test tests/e2e/character_detail_saved_glb.spec.ts`
- `make -C /opt/MediaCreator lint`
- `make -C /opt/MediaCreator typecheck`

## Artifact checks
- `tests/api/test_character_creation_from_classified_photoset.py` proved:
  - a photoset with only rejected entries returns `400`
  - two photosets with the same label create two different character public IDs
  - saved character history keeps:
    - `accepted_entry_public_ids`
    - `body_entry_public_ids`
    - `lora_entry_public_ids`
- `tests/api/test_saved_3d_output_contract.py` proved:
  - `POST /api/v1/exports/characters/{public_id}/preview` returns `202` with queued job metadata
  - the job row exists immediately after queueing with `output_asset_id` set and no fake `output_storage_object_id`
  - after worker execution, the preview storage row exists as `character-preview-glb`
  - the saved GLB file exists on disk before the API reports `preview_glb.status = available`
  - the completed preview job points `output_storage_object_id` at the real saved GLB storage row
  - reconstruction truth uses `body_qualified_entry_count`, not total accepted count, when deciding whether detail prep is available
- `tests/e2e/character_detail_saved_glb.spec.ts` proved:
  - the detail route shows `Preview GLB = not-ready` while the preview job is still queued/running
  - the saved-GLB viewer appears only after the job reaches a terminal state and the route refreshes
  - reload keeps resolving the saved GLB viewer and the `available/completed` output rows

## Results
- `pytest -q tests/api/test_character_creation_from_classified_photoset.py`: `2 passed`
- `pytest -q tests/api/test_saved_3d_output_contract.py`: `2 passed`
- `pnpm exec playwright test tests/e2e/character_detail_saved_glb.spec.ts`: `1 passed`
- `make -C /opt/MediaCreator lint`: passed
- `make -C /opt/MediaCreator typecheck`: passed
  - note: mypy emitted the existing informational note `unused section(s): module = ['rembg.*']` without failing the command

## PASS/FAIL/BLOCKED decision
PASS

## Remaining risks
- The browser verification proves truthful queue-to-artifact behavior, but the richer multi-view body capture needed for detail prep is still exercised more directly in backend tests than in the browser path.
- Final GLB/export promotion beyond the saved preview artifact remains later pipeline scope.
