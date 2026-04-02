# Verify master run

Run this only after all build phases complete.

## Objective
Prove that the repaired MediaCreator runtime is:
- headless/LAN-safe
- truthful after upload
- visibly progressing during character generation
- worker-backed for long jobs
- free of fixed-machine runtime IP assumptions

## Required checks
1. static grep for `10.0.0.102`
2. server bind verification
3. browser/API origin verification
4. photoset accepted/rejected verification
5. zero-accepted creation rejection
6. queued preview job semantics
7. worker heartbeat visibility
8. character detail progress panel
9. terminal preview completion or failure visibility
10. focused tests + lint + typecheck

## Output files to write
- `docs/verification/runtime_repair_verify_phase_01.md`
- `docs/verification/runtime_repair_verify_phase_02.md`
- `docs/verification/runtime_repair_verify_phase_03.md`
- `docs/verification/runtime_repair_verify_phase_04.md`
- `docs/verification/runtime_repair_verify_phase_05.md`
- `docs/verification/runtime_repair_final.md`
