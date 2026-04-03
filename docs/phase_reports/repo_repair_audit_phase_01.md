# Repo Repair Audit Phase 01

## Status

PASS

## Goal

Remove false confidence from repo status and output messaging.

## Changes made

- updated [PLANS.md](/opt/MediaCreator/PLANS.md) so the roadmap no longer claims all 26 rebuild phases are `PASS`
- reset the currently overstated roadmap phases to `PARTIAL` where the audited code still falls short:
  - Phase 05: worker/job coverage
  - Phase 18: saved 3D output maturity
  - Phase 25: proof-image generation
  - Phase 26: final-truth/handoff status
- updated [README.md](/opt/MediaCreator/README.md) to state the current route truth:
  - `POST /api/v1/photosets` still returns `201 Created` after inline ingest/QC
  - queued-job behavior is limited to the actual background-job routes
  - current 3D output is a base/proxy GLB plus optional detail-prep artifact
  - proof-image generation is not yet executed end-to-end
- updated [exports.py](/opt/MediaCreator/apps/api/app/services/exports.py) so preview/reconstruction status text explicitly distinguishes:
  - preview/base GLB
  - detail-prep artifact
  - refined mesh claims only when such an artifact exists
- updated [ReconstructionStatus.tsx](/opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx) to surface explicit saved-3D stage wording in the operator UI

## Pre-verification evidence

- [photosets.py](/opt/MediaCreator/apps/api/app/api/routes/photosets.py) still declares `status_code=201`
- the Phase 01 file-map anchors in `PLANS.md`, `README.md`, and `exports.py` were still structurally recognizable and were repaired in place

## Verification summary

- `apps/api/tests/test_exports_api.py`: passed
- `apps/web/tests/unit/reconstruction-status.test.tsx`: passed
- `make lint`: passed
- `make typecheck`: passed
