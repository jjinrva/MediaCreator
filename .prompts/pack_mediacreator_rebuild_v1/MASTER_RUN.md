
# MASTER_RUN.md

## Mission

Build **MediaCreator** from scratch in this empty folder as a polished, single-user application that can:
- ingest a guided photoset
- prepare images for training and 3D
- create a realistic riggable character
- persist numeric body and pose controls
- create a LoRA from the photoset
- create a GLB/Blender export
- build wardrobe assets
- render controlled character-driven motion and simple video
- generate images/clips from tagged characters
- keep history, lineage, outputs, and storage truthful

## Hard constraints

- Use the exact stack frozen in `STACK_DECISIONS.md`
- Use the source list in `SOURCES.md`
- Use the shared experts under `/experts`
- Complete phases in order
- Do not invent alternates
- Do not continue past a failed verify phase
- Do not seed runtime with fake data
- Keep the product single-user in this rebuild
- Always prefer NAS-backed canonical storage for heavy assets and models

## Before coding

Read in this order:
1. `/AGENTS.md`
2. `/PLANS.md`
3. `/.prompts/pack_mediacreator_rebuild_v1/SOURCES.md`
4. `/.prompts/pack_mediacreator_rebuild_v1/STACK_DECISIONS.md`
5. `/.prompts/pack_mediacreator_rebuild_v1/PHASE_SUMMARY.md`
6. `/.prompts/pack_mediacreator_rebuild_v1/RUN_ORDER.md`

## Working method

For each phase:
1. Read the phase build file.
2. Read the experts named in the phase build file.
3. Build only what the phase allows.
4. Update `docs/phase_reports/phase_##.md`.
5. Read the paired phase verify file.
6. Run the paired verification.
7. Update `docs/verification/phase_##_verify.md`.
8. Only continue if the phase is PASS.

## Required report discipline

At the end of every phase, write:
- what changed
- exact commands run
- exact tests run
- pass/fail
- remaining risks
- whether the next phase may start

## If blocked

Stop immediately and write `CODEX_BLOCKER.md` with:
- phase number
- blocker summary
- exact command/output
- why the chosen path cannot continue
- the minimum missing dependency or decision
