# Phase 04 verify — character generation progress UI

## Verify with code and commands

### Manual flow
1. open `/studio/characters/new`
2. upload a photoset
3. confirm accepted/rejected counts show
4. build the base character
5. confirm the detail page loads
6. confirm a preview-generation progress card appears
7. while the worker runs, confirm the card updates from queued/running
8. on completion, confirm the GLB preview appears or a clear failure message appears
9. reload and confirm the final state persists

### Failure simulation
- stop the worker before queueing preview generation
- confirm the UI reports stale/offline worker and the job remains queued
- start the worker and confirm progress resumes

### Test gates
- character creation e2e
- new progress e2e
- unit tests for job progress card
- unit tests for updated ingest flow
- unit tests for updated detail page status rendering

## Phase fails if
- the user still cannot tell whether generation is queued/running/failed/completed
- the detail page does not refresh into the final state
- stale worker state is hidden
