# Pack intent

## Why this pack exists

The runtime repair pack improves truth and stability, but the operator still needs a focused implementation pass for the practical goal:

**take uploaded human photos and produce a saved character with a saved 3D output and a saved LoRA-backed proof image.**

This pack treats the intake and output flow as one execution contract. It does not leave classification ambiguous, and it does not let Codex hide behind vague success language.

## Exact problems this pack solves

1. required character label, but duplicate labels are allowed
2. truthful upload and server-side scan progress
3. thumbnail click-to-enlarge inspection
4. person-first intake logic:
   - does the image contain a person?
   - if yes, is it usable for LoRA?
   - if not LoRA-usable, is it still usable for body modeling?
   - if usable for both, tag it as both
5. body-only images without a face must be allowed into the body bucket
6. conservative preprocessing:
   - background removal derivative for body-qualified images
   - mild normalization derivative for LoRA-qualified images
7. create saved characters from accepted inputs only
8. save a real 3D output and a real LoRA-backed proof image
9. force artifact existence checks before any “done” status is shown

## Exact chosen path

- keep MediaCreator’s current architectural direction
- keep FastAPI, Next.js App Router, SQLAlchemy, MediaPipe, Pillow, OpenCV
- keep Blender as the 3D runtime
- keep AI Toolkit as the only local LoRA trainer
- keep job polling, not websockets
- use XHR upload progress in the browser plus job-polling for server scan/classification progress
- require deterministic verify steps after every phase

## What this pack explicitly does not do

- it does not introduce alternate LoRA trainers
- it does not introduce alternate 3D runtimes
- it does not invent fake preview states
- it does not skip verification just because a UI looks plausible
- it does not mark a phase PASS unless the phase verify file passes
