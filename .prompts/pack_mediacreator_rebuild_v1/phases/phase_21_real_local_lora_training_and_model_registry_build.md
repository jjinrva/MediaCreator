# Phase 21 build — Real local LoRA training, model registry, and activation

## Goal

Train a real local LoRA with AI Toolkit, register the artifact, and make the app able to activate that LoRA for generation.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/DATABASE_LINEAGE_AND_STORAGE_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- AI Toolkit
- job worker
- NAS model registry
- ComfyUI LoRA activation

### Source IDs to use for this phase
S40, S37, S38


## Exact chosen path for this phase

- Use **AI Toolkit** as the only local LoRA trainer in this rebuild.
- Register every produced LoRA in the model registry.
- Report training readiness truthfully if AI Toolkit is missing or misconfigured.


## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/lora_training.py
- apps/api/app/models/models_registry.py
- apps/api/app/api/routes/lora.py

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Treat AI Toolkit as the exact local LoRA trainer. Do not add alternate trainers in this rebuild. Build a training job that writes a config, launches AI Toolkit, tracks progress, and registers the output model artifact when finished.

### Step 2
Store all LoRA artifacts on the NAS. Register each artifact with status fields such as working, current, failed, archived. Keep a one-current rule per active character/style combination where appropriate.

### Step 3
Create a backend capability check that reports whether AI Toolkit is installed and configured. If it is not present, the app must say training is unavailable rather than faking a pass.

### Step 4
Create a model registry concept now so the generation phases can activate a specific LoRA deterministically.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_21.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- AI Toolkit integration
- LoRA training job
- model registry
- truthful training capability reporting

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
4. `docs/phase_reports/phase_21.md` is updated with exact commands and results.
