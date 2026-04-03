# Current audit basis

## What has already landed

- `POST /api/v1/photosets` now returns `202` and queues ingest
- `photoset-ingest` now runs through the worker
- label-required and duplicate-label behavior is correct
- QC routing is calibrated for `lora_only`, `body_only`, `both`, `rejected`
- body and LoRA derivatives are generated
- thumbnail enlarge is implemented
- saved 3D truth is aligned to proxy/base GLB plus optional detail-prep

## What remains

- proof-image generation job path is still missing
- generation request storage is still not execution
- placeholder workflow JSONs still exist
- generation readiness can still be overstated
- final verify/handoff reports are stale relative to the Phase 05 stop
