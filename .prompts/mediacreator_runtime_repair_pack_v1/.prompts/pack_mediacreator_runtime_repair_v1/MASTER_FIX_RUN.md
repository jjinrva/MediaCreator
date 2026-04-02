# MediaCreator runtime repair — master run

## Goal

Repair the current MediaCreator runtime so the existing character workflow is actually usable on a headless LAN machine.

By the end of this pack:

1. API and web still bind to `0.0.0.0`
2. runtime code no longer assumes one fixed LAN IP
3. upload/QC remains synchronous and truthful
4. photoset acceptance is explicit and failed QC entries do not flow into character creation
5. long-running character-generation work is queue-only and uses the worker
6. the UI shows real progress for character generation
7. the operator can tell when the worker is stale/offline
8. the character detail route surfaces generation status and completion honestly
9. docs/tests match the runtime contract

## Required experts
- `/experts/HEADLESS_NETWORK_AND_ORIGIN_EXPERT.md`
- `/experts/WORKER_ORCHESTRATION_AND_PROGRESS_EXPERT.md`
- `/experts/INGEST_AND_QC_TRUTH_EXPERT.md`

## Required support files
- `.prompts/pack_mediacreator_runtime_repair_v1/AUDIT_REPORT.md`
- `.prompts/pack_mediacreator_runtime_repair_v1/FIX_MATRIX.md`
- `.prompts/pack_mediacreator_runtime_repair_v1/CODE_EXAMPLES.md`
- `.prompts/pack_mediacreator_runtime_repair_v1/SOURCES.md`

## Non-negotiable rules
- Do not add new frameworks.
- Do not replace the current worker model.
- Do not replace the current GLB viewer.
- Do not add websockets in this pack.
- Do not redesign wardrobe/scenes/generation outside what is needed for shared job-progress patterns.
- Do not leave any runtime hardcoded `10.0.0.102` values in code.
- Do not execute long-running jobs inline inside request handlers.
- Do not let failed-QC photos become accepted character sources.

## Required phase order
1. `phase_01_network_and_api_origin_hardening_build.md`
2. `phase_01_network_and_api_origin_hardening_verify.md`
3. `phase_02_photoset_acceptance_and_ingest_truth_build.md`
4. `phase_02_photoset_acceptance_and_ingest_truth_verify.md`
5. `phase_03_async_job_execution_and_worker_heartbeat_build.md`
6. `phase_03_async_job_execution_and_worker_heartbeat_verify.md`
7. `phase_04_character_generation_progress_ui_build.md`
8. `phase_04_character_generation_progress_ui_verify.md`
9. `phase_05_regression_verification_and_docs_build.md`
10. `phase_05_regression_verification_and_docs_verify.md`

## Deliverables
- runtime fixes in the repo
- updated tests
- `docs/phase_reports/runtime_repair_phase_01.md`
- `docs/phase_reports/runtime_repair_phase_02.md`
- `docs/phase_reports/runtime_repair_phase_03.md`
- `docs/phase_reports/runtime_repair_phase_04.md`
- `docs/phase_reports/runtime_repair_phase_05.md`
- `docs/verification/runtime_repair_verify_phase_01.md`
- `docs/verification/runtime_repair_verify_phase_02.md`
- `docs/verification/runtime_repair_verify_phase_03.md`
- `docs/verification/runtime_repair_verify_phase_04.md`
- `docs/verification/runtime_repair_verify_phase_05.md`

## Final acceptance
This pack is complete only when:
- upload → QC → build base character → preview generation progress → preview available
works end to end from a browser on the LAN, without a fixed-machine IP assumption and without silent background ambiguity.
