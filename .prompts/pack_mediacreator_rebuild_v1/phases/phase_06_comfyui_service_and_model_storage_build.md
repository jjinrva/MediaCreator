# Phase 06 build — ComfyUI service, model storage, and generation capability checks

## Goal

Add ComfyUI as the local generation engine and make model storage/versioning live on the NAS with truthful capability reporting.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- ComfyUI
- ComfyUI-Manager
- filesystem/NAS
- FastAPI capability reporting

### Source IDs to use for this phase
S37, S38, S39, S40, S41, S42


## Exact chosen path for this phase

- ComfyUI is a **separate local service**, not code embedded inside the FastAPI app.
- ComfyUI workflows live under `workflows/comfyui/` and are versioned JSON files.
- Model storage points to the NAS by default.
- Capability reporting is mandatory before any generation UI claims readiness.


## Files and directories this phase is allowed to create or modify first

- workflows/comfyui
- apps/api/app/services/generation_provider.py
- apps/api/app/api/routes/system.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Treat ComfyUI as a separate local service. The app must not pretend generation is available until it can detect the ComfyUI service, required models, and at least one known-good workflow file.

### Step 2
Create a backend capability service that reports generation status truthfully: unavailable, partially configured, or ready. Surface the same truth in the API and later in the UI.

### Step 3
Put all ComfyUI model roots on the NAS by default. Document exactly where checkpoints, LoRAs, embeddings, VAEs, and workflow JSON files live. Do not hard-code user-specific paths.

### Step 4
Add a `workflows/comfyui/` folder now with versioned workflow JSON placeholders. The workflow names and purpose must be documented and stable from the start.

### Step 5
Add a backend service that validates the presence of the ComfyUI base URL and the expected workflow/model paths. This phase does not need to generate final images yet; it needs truthful capability checks and storage conventions.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_06.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- ComfyUI capability service
- workflow folder contract
- system status route
- NAS model path contract

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
4. `docs/phase_reports/phase_06.md` is updated with exact commands and results.
