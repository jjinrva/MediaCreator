# RUN_ORDER.md

Execute phases in this exact order:

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_01_workspace_bootstrap_build.md`
2. Execute the build document for Phase 01
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_01_workspace_bootstrap_verify.md`
4. Execute the verify document for Phase 01
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_02_local_infrastructure_and_containers_build.md`
2. Execute the build document for Phase 02
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_02_local_infrastructure_and_containers_verify.md`
4. Execute the verify document for Phase 02
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_03_storage_layout_and_nas_paths_build.md`
2. Execute the build document for Phase 03
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_03_storage_layout_and_nas_paths_verify.md`
4. Execute the verify document for Phase 03
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_04_database_ids_lineage_migrations_build.md`
2. Execute the build document for Phase 04
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_04_database_ids_lineage_migrations_verify.md`
4. Execute the verify document for Phase 04
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_05_job_orchestration_and_worker_foundation_build.md`
2. Execute the build document for Phase 05
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_05_job_orchestration_and_worker_foundation_verify.md`
4. Execute the verify document for Phase 05
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_06_comfyui_service_and_model_storage_build.md`
2. Execute the build document for Phase 06
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_06_comfyui_service_and_model_storage_verify.md`
4. Execute the verify document for Phase 06
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_07_ui_shell_design_system_and_accessibility_build.md`
2. Execute the build document for Phase 07
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_07_ui_shell_design_system_and_accessibility_verify.md`
4. Execute the verify document for Phase 07
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_08_guided_capture_assets_and_instructions_build.md`
2. Execute the build document for Phase 08
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_08_guided_capture_assets_and_instructions_verify.md`
4. Execute the verify document for Phase 08
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_09_photoset_ingest_ui_build.md`
2. Execute the build document for Phase 09
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_09_photoset_ingest_ui_verify.md`
4. Execute the verify document for Phase 09
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_10_photo_qc_and_preparation_build.md`
2. Execute the build document for Phase 10
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_10_photo_qc_and_preparation_verify.md`
4. Execute the verify document for Phase 10
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_11_character_asset_registry_and_base_creation_build.md`
2. Execute the build document for Phase 11
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_11_character_asset_registry_and_base_creation_verify.md`
4. Execute the verify document for Phase 11
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_12_character_detail_glb_preview_export_scaffold_build.md`
2. Execute the build document for Phase 12
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_12_character_detail_glb_preview_export_scaffold_verify.md`
4. Execute the verify document for Phase 12
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_13_numeric_body_parameter_model_build.md`
2. Execute the build document for Phase 13
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_13_numeric_body_parameter_model_verify.md`
4. Execute the verify document for Phase 13
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_14_numeric_body_editing_ui_persistence_build.md`
2. Execute the build document for Phase 14
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_14_numeric_body_editing_ui_persistence_verify.md`
4. Execute the verify document for Phase 14
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_15_numeric_limb_pose_and_persistent_state_build.md`
2. Execute the build document for Phase 15
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_15_numeric_limb_pose_and_persistent_state_verify.md`
4. Execute the verify document for Phase 15
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_16_face_expression_parameter_foundation_build.md`
2. Execute the build document for Phase 16
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_16_face_expression_parameter_foundation_verify.md`
4. Execute the verify document for Phase 16
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_17_blender_runtime_rigify_and_export_build.md`
2. Execute the build document for Phase 17
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_17_blender_runtime_rigify_and_export_verify.md`
4. Execute the verify document for Phase 17
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_18_high_detail_3d_reconstruction_refinement_build.md`
2. Execute the build document for Phase 18
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_18_high_detail_3d_reconstruction_refinement_verify.md`
4. Execute the verify document for Phase 18
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_19_texture_skin_and_material_fidelity_build.md`
2. Execute the build document for Phase 19
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_19_texture_skin_and_material_fidelity_verify.md`
4. Execute the verify document for Phase 19
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_20_lora_dataset_curation_and_tagging_build.md`
2. Execute the build document for Phase 20
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_20_lora_dataset_curation_and_tagging_verify.md`
4. Execute the verify document for Phase 20
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_21_real_local_lora_training_and_model_registry_build.md`
2. Execute the build document for Phase 21
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_21_real_local_lora_training_and_model_registry_verify.md`
4. Execute the verify document for Phase 21
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_22_wardrobe_photo_and_ai_generation_build.md`
2. Execute the build document for Phase 22
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_22_wardrobe_photo_and_ai_generation_verify.md`
4. Execute the verify document for Phase 22
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_23_motion_library_retargeting_and_controlled_actions_build.md`
2. Execute the build document for Phase 23
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_23_motion_library_retargeting_and_controlled_actions_verify.md`
4. Execute the verify document for Phase 23
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_24_controlled_video_rendering_build.md`
2. Execute the build document for Phase 24
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_24_controlled_video_rendering_verify.md`
4. Execute the verify document for Phase 24
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_25_tagged_image_video_generation_workspace_build.md`
2. Execute the build document for Phase 25
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_25_tagged_image_video_generation_workspace_verify.md`
4. Execute the verify document for Phase 25
5. If verify fails, stop and write `CODEX_BLOCKER.md`

1. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_26_diagnostics_settings_final_verification_and_handoff_build.md`
2. Execute the build document for Phase 26
3. Read `/.prompts/pack_mediacreator_rebuild_v1/phases/phase_26_diagnostics_settings_final_verification_and_handoff_verify.md`
4. Execute the verify document for Phase 26
5. If verify fails, stop and write `CODEX_BLOCKER.md`

