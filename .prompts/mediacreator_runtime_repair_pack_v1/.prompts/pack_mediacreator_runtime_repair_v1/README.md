# MediaCreator runtime repair pack v1

This pack audits the current checked-in MediaCreator runtime and fixes the issues blocking real use on a headless LAN machine.

This pack is intentionally small and focused. It does **not** redesign the app. It repairs the current implementation so the existing character workflow is truthful, progress is visible, the worker is actually used for long-running work, and fixed-machine IP assumptions are removed.

## Included
- `AUDIT_REPORT.md` — static audit of the current repo
- `FIX_MATRIX.md` — finding → required fix → affected files
- `CODE_EXAMPLES.md` — exact implementation patterns Codex should follow
- `MASTER_FIX_RUN.md` — main build run
- `VERIFY_MASTER_RUN.md` — final verify run
- `phases/` — five ordered build/verify phase docs
- `checklists/VERIFY_CHECKLIST.md` — manual acceptance checklist
- `SOURCES.md` — repo evidence and official docs

## Scope
1. Network/public-origin hardening
2. Photoset acceptance and ingest truth
3. Async job execution + worker heartbeat
4. Character generation progress UX
5. Regression verification and docs

## Out of scope
- wardrobe redesign
- scene composition
- auth/multi-user
- replacing the GLB viewer
- new worker technologies
