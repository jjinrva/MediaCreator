# Phase 05 build — LoRA training, registry, and proof generation

## Phase goal

Produce a truthful LoRA path that trains only from LoRA-qualified images and saves at least one proof image when the runtime is truly capable.

## Experts Codex must use for this phase

- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`

## Exact chosen path

- AI Toolkit is the only local LoRA trainer in this pack.
- The LoRA dataset is built only from `lora_only` and `both`.
- `body_only` images must never enter the LoRA dataset unless they independently pass the LoRA gate.
- Capability must be checked truthfully before training is claimed available.
- When capability is real, train/register a real model artifact and generate at least one proof image from that artifact.
- When capability is not real, stop with a blocker or truthful disabled state. Do not fake a trained result.

## Exact stack and libraries

- AI Toolkit
- existing jobs/worker pattern
- current model registry
- current generation path that can activate a selected LoRA artifact

### Source IDs for this phase
S05, S06, S14

## Exact file areas

Start with these files:

- `apps/api/app/services/lora_dataset.py`
- `apps/api/app/services/lora_training.py`
- `apps/api/app/api/routes/lora.py`
- `apps/api/app/models/models_registry.py`

Inspect generation-routing files only as needed after those.

## Ordered steps

### Step 1 — build the dataset from LoRA-qualified assets only

Create or patch the dataset builder so it consumes only:
- `lora_only`
- `both`

Dataset outputs must include:
- image files
- matching caption files or caption manifest
- source lineage links
- dataset version identifier

**Verification immediately after Step 1**
- add tests that `body_only` and `rejected` assets are excluded
- add tests that dataset version artifacts are written

### Step 2 — truthful capability check

Implement a real capability check for AI Toolkit.

At minimum it must prove:
- the executable or invocation path exists
- required environment pieces for training are present
- the app can distinguish available vs unavailable without guessing

**Verification immediately after Step 2**
- add tests for unavailable capability returning disabled truthfully
- if a lightweight dry-run check exists, add it here

### Step 3 — real training job and registry update

When capability is available:
- queue a real LoRA training job
- write the config and dataset version
- register the artifact on success
- write a failed status on failure
- never set current/active without a real artifact

**Verification immediately after Step 3**
- add tests for registry status transitions
- add a small real-run integration check if the environment can support it

### Step 4 — proof image generation

Use the newly registered or updated active LoRA artifact to generate at least one proof image.

Rules:
- save the prompt and visible prompt expansion
- save the proof image artifact
- link the proof image back to the LoRA artifact and character

**Verification immediately after Step 4**
- add a test that the saved proof image exists and is lineage-linked
- assert the UI/API cannot say proof generation succeeded without the file

## Pass/fail criteria

### PASS
- only LoRA-qualified assets enter the dataset
- capability is reported truthfully
- a real artifact is required for success language
- at least one proof image is saved when capability is real

### FAIL
- `body_only` assets enter the LoRA dataset
- AI Toolkit availability is guessed instead of checked
- registry marks current/working without a file artifact
- proof-image success is reported without a saved output

## Deliverables

- patched LoRA dataset builder
- truthful capability check
- patched training/registry path
- proof-image generation path
- targeted dataset/training/proof tests

## Forbidden scope

- do not add an alternate trainer
- do not use mocked training success as real completion
- do not skip the proof-image step when capability is real

## Documentation Codex must update in this phase

- `docs/phase_reports/intake_saved_outputs_phase_05.md`
- `docs/verification/intake_saved_outputs_phase_05_verify.md`
- `docs/architecture/lora_dataset_and_proof_contract.md`

## Exit condition

The phase may stop only when the paired verify file can prove either:
- real capability with real artifact and real proof image, or
- truthful blocked/unavailable state with exact blocker evidence.
