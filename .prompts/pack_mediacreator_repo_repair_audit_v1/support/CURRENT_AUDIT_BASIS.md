# Current audit basis

This pack is based on the extracted snapshot from:

- `MediaCreator-review-slim-20260402-235253.zip`
- snapshot identifier: `4c95e6c06107c90f35b802b1292b0e200157db26`

## Important note

Before editing code:

1. open every file listed in `FILE_AND_LINE_MAP.md`
2. confirm the lines are still structurally recognizable
3. if the file has moved or materially changed, update the local audit notes
4. do not skip the repair because of drift
5. do not silently assume the drift fixed the problem

## Main conclusions

- the repo status is overstated
- ingest is synchronous despite async claims
- the worker lacks a real `photoset-ingest` executor
- 3D output is proxy/base-level, not refined reconstruction
- generation requests are stored, but proof-image generation is not executed
