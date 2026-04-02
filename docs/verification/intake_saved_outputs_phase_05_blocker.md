# Phase 05 Blocker
`phase_05_lora_training_registry_and_proof_generation`

## Blocking commands
- `which ai-toolkit`
  - result: no output
- `printenv MEDIACREATOR_AI_TOOLKIT_BIN`
  - result: no output
- `curl -sS http://127.0.0.1:8010/api/v1/system/status`
  - result:
    - `ai_toolkit.status = unavailable`
    - `ai_toolkit.missing_requirements = ["ai_toolkit_missing"]`
    - `generation.status = unavailable`
    - `generation.missing_requirements = ["comfyui_base_url_missing", "checkpoint_files_missing", "vae_files_missing"]`

## Why Phase 05 cannot PASS here
- The pack requires a real AI Toolkit LoRA artifact before training can be called successful.
- The pack also requires at least one saved proof image when capability is real.
- This machine currently lacks the trainer binary and also lacks a ready generation runtime for proof images.

## Required next action
1. Install AI Toolkit and make it available on `PATH`, or set `MEDIACREATOR_AI_TOOLKIT_BIN` to the real executable.
2. Configure `MEDIACREATOR_COMFYUI_BASE_URL` for a reachable ComfyUI service.
3. Populate NAS-backed checkpoint and VAE files under:
   - `/mnt/nas/mediacreator/models/checkpoints`
   - `/mnt/nas/mediacreator/models/vaes`
4. Rerun the Phase 05 verify commands after those dependencies are real.
