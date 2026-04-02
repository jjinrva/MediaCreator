# Run order

## Read order

1. `README.md`
2. `PACK_INTENT.md`
3. `SOURCES.md`
4. `support/CURRENT_AUDIT_BASIS.md`
5. `support/PATCH_SCOPE_AND_FILE_MAP.md`
6. `support/PHOTO_CLASSIFICATION_DECISION_TREE.md`
7. `support/OUTPUT_AND_LINEAGE_CONTRACT.md`
8. `support/CODEX_TRUTH_AND_FAILURE_POLICY.md`
9. `reports/ACCEPTANCE_CRITERIA.md`
10. `reports/PATCH_MATRIX.md`

## Execution rule

Later phases are forbidden until the current phase passes its verify file.

## Ordered phase list

1. `phase_01_backend_ingest_progress_and_person_first_routing_build.md`
2. `phase_01_backend_ingest_progress_and_person_first_routing_verify.md`
3. `phase_02_frontend_intake_truth_label_and_thumbnail_preview_build.md`
4. `phase_02_frontend_intake_truth_label_and_thumbnail_preview_verify.md`
5. `phase_03_preprocessing_derivatives_and_dataset_manifests_build.md`
6. `phase_03_preprocessing_derivatives_and_dataset_manifests_verify.md`
7. `phase_04_base_character_creation_and_saved_3d_output_build.md`
8. `phase_04_base_character_creation_and_saved_3d_output_verify.md`
9. `phase_05_lora_training_registry_and_proof_generation_build.md`
10. `phase_05_lora_training_registry_and_proof_generation_verify.md`
11. `phase_06_end_to_end_acceptance_and_truth_gates_build.md`
12. `phase_06_end_to_end_acceptance_and_truth_gates_verify.md`

## Staging rule

Only the current phase and files it explicitly references may be staged to Codex. Do not stage future phase files early.
