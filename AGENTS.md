# AGENTS.md

## Permanent mission

Build **MediaCreator** as a polished, truthful, single-user application that is architected for future multi-user support.

## Permanent architecture rules

### Backend
- FastAPI for HTTP API
- Pydantic v2 for request/response schemas
- SQLAlchemy 2 declarative ORM
- Alembic for migrations
- PostgreSQL 16 as the source of truth
- Python 3.12 for the backend runtime
- background work is orchestrated through database-backed jobs and a dedicated worker process
- use `FOR UPDATE SKIP LOCKED` dequeue semantics for worker pickup

### Frontend
- Next.js App Router
- React
- TypeScript
- shared accessible primitives
- Radix Slider and Tooltip for numeric controls and hover help
- use the existing `fetch`/API client pattern; do not add Axios unless a documented blocker requires it

### 3D
- Blender 4.5 LTS is the authoritative DCC/runtime tool
- Rigify is the rig generation baseline
- GLB is the primary web preview/export format
- `<model-viewer>` is the primary preview component in the web app
- do not replace the web 3D viewer unless a phase explicitly authorizes it

### Diffusion / LoRA / Image generation
- ComfyUI is the generation orchestration layer
- AI Toolkit is the local LoRA training backend
- Civitai public REST integration is optional but supported in later phases
- all models live on NAS-backed storage by default

## Permanent product rules

- No runtime sample/demo data
- Every meaningful change writes history
- Every important asset has lineage
- Numeric body edits and numeric pose edits are first-class persisted state
- Every slider and text control gets an info icon/tooltip
- If something is not implemented, the UI must say so truthfully
- Character-driven animation must control the character rig; do not fake the requirement by substituting one-shot AI video generation

## Execution rules for Codex

1. Read the current phase build document.
2. Read the paired phase verify document.
3. Use the experts named in the phase document.
4. Follow the exact chosen tool/library path.
5. Complete the build steps in order.
6. Run the exact verify steps before moving on.
7. Update:
   - `docs/phase_reports/phase_##.md`
   - `docs/verification/phase_##_verify.md`
8. If blocked, stop and write:
   - `CODEX_BLOCKER.md`

## Reporting format

At the end of each phase, report:
- PASS or FAIL
- what changed
- exact commands run
- tests that passed
- remaining risks
