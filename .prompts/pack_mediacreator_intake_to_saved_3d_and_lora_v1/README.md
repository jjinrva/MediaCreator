# MediaCreator intake to saved 3D + LoRA pack

## What this pack does

This pack patches the first operator journey that matters right now:

1. enter a required character label,
2. upload a photoset,
3. see truthful upload and scan progress,
4. see each photo classified as `lora_only`, `body_only`, `both`, or `rejected`,
5. enlarge any thumbnail to inspect it,
6. create a saved character from accepted assets only,
7. generate and save a real 3D character output,
8. train and register a real LoRA when the runtime is capable,
9. save at least one proof image generated from that LoRA,
10. refuse to claim completion unless deterministic verification passes.

## Target app

- MediaCreator
- follow-on work after the current runtime repair effort
- uses the existing repo prompt-pack contract
- uses shared experts from `/experts`

## Why this pack exists

The current operator pain is concentrated in intake truth and output truth:

- body-only images are being rejected because they do not show a face,
- clearly usable images are being mislabeled as blurry,
- upload progress is opaque,
- thumbnails do not expand for inspection,
- the operator cannot trust which photos are going to LoRA vs 3D,
- completion can be overstated unless artifacts are checked.

## Success looks like this

A single operator can complete the following without ambiguity:

- upload a labeled photoset,
- watch progress move from transfer to scan to classification,
- understand why each photo was accepted or rejected,
- click a thumbnail to inspect the larger image and its QC reasons,
- create a saved character even if the label duplicates an existing one,
- get a saved 3D output when body-qualified inputs exist,
- get a saved LoRA and a proof image when AI Toolkit is actually available,
- see explicit FAIL/BLOCKED state when dependencies or artifacts are missing.

## What this pack does not solve

- wardrobe pipelines
- motion pipelines
- composer / scene UX
- multi-user auth
- new research stacks beyond the existing MediaCreator choices
- replacing Blender, ComfyUI, AI Toolkit, or the current GLB viewer
