# Phase 05 build — generation proof-image runtime unblock

## Goal

Close the remaining generation gap without breaking already-correct intake/QC/base-3D work.

## Required changes

### 1. Add a real proof-image job contract
- add a new job payload to `apps/api/app/services/jobs.py`
- use an explicit kind such as `generation-proof-image`
- include enough payload data to reproduce the request truthfully:
  - generation request public id
  - character public id if present
  - selected local LoRA registry id if present
  - selected external LoRA registry id if present
  - expanded prompt
  - workflow id/path
  - expected output path
  - output root class

### 2. Add a real queue path
- extend generation request handling so the ready case can queue proof-image execution
- preserve the blocked/staged case when runtime is not ready
- do not convert the blocked case into fake success

### 3. Add a real worker execution branch
- add an explicit worker branch in `apps/api/app/services/jobs.py`
- do not overload an unrelated job type
- on success:
  - persist the proof image as a storage object
  - complete the job
  - record lineage/history
- on failure:
  - fail the job
  - preserve a truthful error summary

### 4. Add a provider execution service
- create a dedicated service for proof-image execution
- call the actual ComfyUI endpoint or contract used by the repo
- record:
  - request id
  - workflow id/path
  - provider status
  - model references
  - output image path
- refuse to claim success unless the saved image file exists

### 5. Tighten generation capability truth
- update `apps/api/app/services/generation_provider.py`
- do not let file presence alone satisfy workflow readiness
- validate that required workflow files are non-placeholder and runnable enough for the claimed capability
- placeholder graphs with `nodes: []` must keep capability blocked
- only return `ready` when:
  - service is reachable
  - workflow files exist
  - workflow files pass validation
  - checkpoint and VAE files exist
  - proof-image execution path exists in repo code

### 6. Replace or explicitly block placeholder workflows
- either:
  - replace `workflows/comfyui/text_to_image_v1.json`
  - replace `workflows/comfyui/character_refine_img2img_v1.json`
  with minimal runnable graphs
- or keep them blocked and make the capability report that truth clearly
- do not keep empty `nodes: []` while still allowing `ready`

### 7. Fix the tests
- update `apps/api/tests/test_generation_provider.py`
- placeholder workflow files must not produce `ready`
- add tests for:
  - blocked placeholder workflow state
  - ready validated workflow state
  - proof-image job path in the ready runtime case
  - blocked case with no artifact

### 8. Refresh stale final truth only after the real pass
- only after verify passes:
  - refresh `docs/verification/final_verify_matrix.md`
  - refresh `docs/handoff/overnight_acceptance_report.md`
- if verify is blocked, do not rewrite those files to sound complete

## Safeguards

- preserve `POST /api/v1/photosets` async behavior
- preserve body-only acceptance without face
- preserve thumbnail enlarge
- preserve current 3D truth wording
- do not let Codex mark the phase done without a saved proof-image artifact in the ready case
