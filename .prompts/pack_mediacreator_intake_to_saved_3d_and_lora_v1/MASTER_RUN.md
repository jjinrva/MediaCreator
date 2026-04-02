# MediaCreator intake to saved 3D + LoRA — master run

## Goal

Patch the real MediaCreator operator flow so the app can take a labeled photoset and produce truthful, saved outputs.

By the end of this pack:

1. the operator must enter a character label before ingest starts
2. duplicate labels are allowed; uniqueness belongs to IDs, not the human-facing label
3. upload progress must show both transfer and server-side scan/classification state
4. every photo must land in exactly one visible bucket:
   - `lora_only`
   - `body_only`
   - `both`
   - `rejected`
5. a body shot with no face must be allowed into the body bucket when body evidence is strong enough
6. thumbnails must enlarge on click and expose acceptance reasons
7. only accepted assets may flow into character creation, dataset creation, or 3D creation
8. body-qualified inputs must produce a saved 3D character output when minimum body criteria are met
9. LoRA-qualified inputs must produce a saved LoRA and at least one saved proof image when AI Toolkit is truly available
10. no screen may say complete unless the corresponding file artifact and database/output record both exist

## Required experts

- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/DIFFUSION_COMFYUI_AND_LORA_EXPERT.md`
- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read them before changing code. Do not treat them as optional.

## Required support files

- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/support/CURRENT_AUDIT_BASIS.md`
- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/support/PATCH_SCOPE_AND_FILE_MAP.md`
- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/support/PHOTO_CLASSIFICATION_DECISION_TREE.md`
- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/support/OUTPUT_AND_LINEAGE_CONTRACT.md`
- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/support/CODEX_TRUTH_AND_FAILURE_POLICY.md`
- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/reports/ACCEPTANCE_CRITERIA.md`
- `.prompts/pack_mediacreator_intake_to_saved_3d_and_lora_v1/reports/PATCH_MATRIX.md`

## Non-negotiable rules

- Do not create option-based prompts.
- Do not change the prompt-pack folder contract.
- Do not replace the current GLB viewer stack.
- Do not add websockets in this pack.
- Do not add an alternate LoRA trainer.
- Do not add an alternate 3D pipeline.
- Do not reject a body-only image solely because no face is visible.
- Do not accept any image into the LoRA bucket unless the image passes the LoRA-specific checks.
- Do not say “complete”, “done”, “working”, or “generated” unless verification and artifact checks prove it.
- Do not continue to a later phase if the current verify phase fails.
- If a dependency is missing and cannot be made operational, write a blocker report and stop. Do not claim a partial success as full completion.

## Required phase order

1. `phases/phase_01_backend_ingest_progress_and_person_first_routing_build.md`
2. `phases/phase_01_backend_ingest_progress_and_person_first_routing_verify.md`
3. `phases/phase_02_frontend_intake_truth_label_and_thumbnail_preview_build.md`
4. `phases/phase_02_frontend_intake_truth_label_and_thumbnail_preview_verify.md`
5. `phases/phase_03_preprocessing_derivatives_and_dataset_manifests_build.md`
6. `phases/phase_03_preprocessing_derivatives_and_dataset_manifests_verify.md`
7. `phases/phase_04_base_character_creation_and_saved_3d_output_build.md`
8. `phases/phase_04_base_character_creation_and_saved_3d_output_verify.md`
9. `phases/phase_05_lora_training_registry_and_proof_generation_build.md`
10. `phases/phase_05_lora_training_registry_and_proof_generation_verify.md`
11. `phases/phase_06_end_to_end_acceptance_and_truth_gates_build.md`
12. `phases/phase_06_end_to_end_acceptance_and_truth_gates_verify.md`

## Deliverables

- patched intake API and UI
- classification bucketing for LoRA/body/both/rejected
- enlarged thumbnail inspection UI
- saved photoset + derivative lineage
- saved character record with duplicate labels allowed
- saved GLB output and truthful progress/status
- saved LoRA artifact and saved proof image when capability is real
- deterministic tests and verification reports
- blocker reports where capability is not actually available

## Final acceptance

This pack is complete only when a repeated end-to-end run proves the following:

- labeled photos upload successfully,
- progress is understandable,
- body-only images can still support 3D,
- accepted photos are routed to the correct downstream purpose,
- a saved 3D character artifact exists,
- a saved LoRA artifact and a saved proof image exist when the trainer is operational,
- no completion state is shown without real artifacts.
