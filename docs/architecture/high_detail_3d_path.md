# High-Detail 3D Path

Phase 18 introduces the first truthful contract for higher-fidelity character reconstruction without breaking the riggable character requirement.

## Two-stage path

MediaCreator follows one path only:

1. Fit a riggable parametric human base with the SMPL-X family and keep Blender/Rigify as the downstream runtime for attachment, posing, and GLB export.
2. Add a COLMAP-backed detail-prep stage only when the capture set is strong enough to justify it.

The riggable base remains authoritative. A later detail stage may improve geometry and appearance, but it must not replace the controllable base mesh with an uncontrolled output.

## Current Phase 18 implementation

Phase 18 ships the service contract and truthful status reporting:

- the reconstruction route always aims to produce or reuse the riggable base GLB
- the current implementation writes a `detail-prep` manifest only when the character has at least 6 accepted reference images
- the manifest is not a claim that a refined mesh already exists
- the UI reports `riggable-base-only` or `riggable-base-plus-detail-prep` exactly as stored artifacts allow

This keeps the current system honest while establishing the job/output/history contract needed for later SMPL-X fitting and COLMAP-backed refinement.

## Capture requirements

Research-grade fidelity needs more than the Phase 09 ingest minimum:

- 60 to 120+ sharp photos are the practical target for serious reconstruction work
- overlapping views around the full body are required, not just front/back hero shots
- stable lighting matters because texture projection and material cleanup get much worse under changing light
- the subject should stay consistent across the set so the detail stage does not have to reconcile pose drift or wardrobe drift

The current automatic gate is intentionally coarse. It checks only whether the accepted capture count is large enough to justify writing the detail-prep artifact. Human review for overlap, lighting, and consistency still matters.

## Current job/output contract

`POST /api/v1/exports/characters/{character_public_id}/reconstruction` writes:

- a `high-detail-reconstruction` job row
- a real riggable base GLB if one is missing
- a `character-detail-prep-manifest` storage object only when the capture set qualifies
- `reconstruction.completed` history
- `reconstruction.detail_prep_generated` history when the detail-prep artifact exists

The detail route exposes the current strategy, detail level, and artifact availability through the outputs payload so the user sees the real state instead of optimistic placeholders.
