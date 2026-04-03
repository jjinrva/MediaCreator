# Repo Repair Audit Phase 05 Blocker

## Status

BLOCKED

## Why execution stopped

Phase 05 requires a truthful proof-image generation path. The current repo and runtime cannot satisfy that contract.

## Concrete blockers

1. No proof-image job payload or worker branch exists
   - [jobs.py](/opt/MediaCreator/apps/api/app/services/jobs.py) has no generation-proof job kind and no execution branch for it.

2. Generation requests are only stored
   - [prompt_expansion.py](/opt/MediaCreator/apps/api/app/services/prompt_expansion.py#L526) records a `generation-request` asset and history only.

3. ComfyUI runtime is not operational
   - `/api/v1/system/status` reports generation `unavailable`
   - base URL is missing
   - checkpoint files are missing
   - VAE files are missing

4. AI Toolkit is not installed
   - `which ai-toolkit` returns no path

5. The repo workflows are placeholders, not runnable proof-image graphs
   - [text_to_image_v1.json](/opt/MediaCreator/workflows/comfyui/text_to_image_v1.json#L6)
   - [character_refine_img2img_v1.json](/opt/MediaCreator/workflows/comfyui/character_refine_img2img_v1.json#L6)

## What would be required to unblock

- add a real generation-proof-image job payload plus explicit worker execution branch
- add a truthful provider execution path that writes a saved proof image artifact
- persist storage-object and request-lineage links for that artifact
- replace the placeholder ComfyUI workflows with runnable graphs
- configure a reachable ComfyUI base URL and provide checkpoint/VAE files
- install AI Toolkit if local LoRA-backed proof generation is expected

## Stop rule applied

The pack requires stopping when runtime dependencies required for proof-image generation cannot be made operational without lying about artifacts or execution. That condition is met here.
