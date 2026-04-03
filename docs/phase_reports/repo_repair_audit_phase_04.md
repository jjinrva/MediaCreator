# Repo Repair Audit Phase 04

## Status

PASS

## Goal

Make the saved 3D output path truthful about what exists now: base/proxy GLB, optional detail-prep artifact, and no claimed refined mesh.

## Changes made

- no additional code edits were required in this phase because the current tree already matched the Phase 04 truth contract
- verified that the existing export payload and reconstruction UI already distinguish:
  - base/proxy GLB
  - detail-prep artifact
  - absent refined mesh
- verified that character creation still keeps the preview export action explicit and test-backed through the existing UI flow

## Pre-verification evidence

- [exports.py](/opt/MediaCreator/apps/api/app/services/exports.py#L180) only derives reconstruction detail levels as `riggable-base-plus-detail-prep`, `riggable-base-only`, or `not-started`
- [exports.py](/opt/MediaCreator/apps/api/app/services/exports.py#L202) and [exports.py](/opt/MediaCreator/apps/api/app/services/exports.py#L213) explicitly say no refined mesh is claimed yet
- [reconstruction.py](/opt/MediaCreator/apps/api/app/services/reconstruction.py#L234) persists `refined_detail_mesh_generated: False` in the detail-prep manifest contract
- [ReconstructionStatus.tsx](/opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx#L24) renders the saved 3D stage as base/proxy plus optional detail-prep and only mentions refined mesh in the dedicated `refined-mesh-available` case
- [character-import.test.tsx](/opt/MediaCreator/apps/web/tests/unit/character-import.test.tsx#L120) still proves the create-character flow explicitly calls the preview export route after character creation

## Verification summary

- targeted saved-3D API proof passed:
  - `tests/test_saved_3d_output_contract.py`
  - `tests/test_blender_export_api.py`
  - `tests/test_reconstruction_api.py`
- targeted saved-3D UI proof passed:
  - `apps/web/tests/unit/reconstruction-status.test.tsx`
  - `apps/web/tests/unit/character-import.test.tsx`
- `make lint`: passed
- `make typecheck`: passed
