# Phase 25 build — Tagged image/video generation workspace and external LoRA use

## Goal

Build the standalone generation workspace where users can prompt with `@character`, optionally activate local/external LoRAs, and see the full expanded prompt for now.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- ComfyUI
- Civitai REST API
- prompt expansion service
- NAS model registry

### Source IDs to use for this phase
S37, S38, S40, S41, S42


## Exact chosen path for this phase

- Build a separate generation workspace away from the core 3D editing surfaces.
- Expand `@character` handles into visible full prompts for this rebuild.
- Imported Civitai LoRAs must become internal registry entries before they are usable.


## Files and directories this phase is allowed to create or modify first

- apps/web/app/studio/generate
- apps/api/app/services/prompt_expansion.py
- apps/api/app/api/routes/generation.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create a generation workspace separate from the 3D character edit screens. This workspace can generate standalone images and simple clips, but it must also support `@character` references that expand to the selected character’s visible prompt recipe.

### Step 2
Make prompt expansion visible in this rebuild. If the user types `@hang standing on a bridge`, the UI should show the full expanded prompt that will be sent into the generation workflow.

### Step 3
Support local LoRA activation through the model registry. Support optional discovery/import of external LoRAs through the Civitai REST API in a later-safe, registry-backed way. Imported models must still become internal registry entries before use.

### Step 4
Keep all model files on the NAS and all generation workflows versioned under `workflows/comfyui`.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_25.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- generation workspace
- prompt expansion service
- local/external LoRA activation path

## What Codex must not do in this phase


- Do not create parallel implementations of the same concept.
- Do not add auth or multi-user logic in this phase unless the phase explicitly says to create future-ready fields only.
- Do not seed runtime screens with demo/sample data.
- Do not change the chosen stack.
- Do not continue to the next phase until this phase passes verify.


## Exit condition for the build phase

The build phase may stop only when:
1. the phase deliverables exist,
2. the changed code is coherent,
3. the paired verify file has enough hooks to test the phase honestly,
4. `docs/phase_reports/phase_25.md` is updated with exact commands and results.
