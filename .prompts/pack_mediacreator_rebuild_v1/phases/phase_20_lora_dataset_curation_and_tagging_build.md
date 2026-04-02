# Phase 20 build — LoRA dataset curation, prompt tagging, and training inputs

## Goal

Prepare the best possible training set from the accepted photoset and define exactly how MediaCreator tags and expands character prompts.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Python image prep
- metadata tagging
- AI Toolkit-compatible dataset format

### Source IDs to use for this phase
S40, S41, S42



## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/lora_dataset.py
- docs/architecture/lora_dataset_contract.md

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create the dataset-curation service that selects accepted images, builds training manifests, and attaches explicit caption/tag data. This service should be strict about which inputs are allowed into the LoRA dataset.

### Step 2
Define the character tagging rules now. The character handle, visible descriptor tags, and future prompt expansion rules must be explicit and versioned. In this rebuild, `@character` expansion is visible in the UI so the generated prompt can be audited.

### Step 3
Write the dataset outputs to NAS-backed storage with one folder per training dataset version. Keep source references and lineage links back to the original capture set.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_20.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- LoRA dataset service
- dataset manifest format
- prompt-handle contract

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
4. `docs/phase_reports/phase_20.md` is updated with exact commands and results.
