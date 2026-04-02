# Current audit basis

This pack is grounded in the bundle contents plus explicit operator-reported failures.

## Bundle-derived basis

The handoff bundle states that MediaCreator already contains real implementation for:

- photoset upload and QC
- base character creation
- worker/job foundations
- GLB preview/detail route
- LoRA training surfaces
- 3D reconstruction/runtime surfaces

The same bundle also identifies structural weaknesses around:

- progress visibility
- honest job status
- accepted/rejected gating
- generation truth
- worker liveness and stalled states

## User-reported live failures to treat as high priority

1. clear images are being marked too blurry
2. body shots with no visible face are being rejected
3. upload can sit on a vague “uploading photoset” state
4. clicking a thumbnail does not enlarge the image
5. the operator needs automatic routing into LoRA and/or 3D suitability
6. the operator wants saved 3D characters by the end of the run
7. the operator wants Codex prevented from claiming success without proof

## Required honesty rule

This pack was written from the bundle and the operator-reported failures.
Codex must still inspect the current repo state before editing.
If any expected file area is missing or materially different, Codex must write a blocker note instead of pretending the pack mapped cleanly.
