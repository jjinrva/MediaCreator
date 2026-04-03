# Repo Repair Audit Phase 03

## Status

PASS

## Goal

Repair QC acceptance and routing so intake truthfully separates `lora_only`, `body_only`, `both`, and `rejected`.

## Changes made

- updated [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py) to keep person-first gating, calibrate body blur to `55.0`, and split QC routing through `_qc_metrics(...)` plus `_qc_report_from_signals(...)`
- added explicit persisted sub-check flags in [photosets.py](/opt/MediaCreator/apps/api/app/schemas/photosets.py) and mirrored them in [CharacterImportIngest.tsx](/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx):
  - `person_detected`
  - `blur_ok_for_lora`
  - `blur_ok_for_body`
  - `exposure_ok_for_lora`
  - `exposure_ok_for_body`
- kept body-only acceptance truthful: a no-face image with strong body evidence now routes to `body_only` instead of being rejected solely for missing face evidence
- added clearer borderline body messages in [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py) so body-qualified images can warn without being mislabeled as failed LoRA images
- added deterministic calibration coverage in [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py)
- updated the affected API and web tests so their persisted payload fixtures match the expanded QC contract and current frontend copy

## Pre-verification evidence

- [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py#L57) sets `MIN_BLUR_FOR_BODY = 55.0`
- [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py#L433) now records explicit QC sub-check metrics, including `person_detected`, `blur_ok_*`, and `exposure_ok_*`
- [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py#L532) now routes through `_qc_report_from_signals(...)`
- [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py#L604) and [photo_prep.py](/opt/MediaCreator/apps/api/app/services/photo_prep.py#L628) now emit borderline body warnings instead of false hard failures
- [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py) covers no-person, `lora_only`, `body_only`, `both`, and borderline body-only routing

## Verification summary

- targeted deterministic QC/backend proof passed:
  - `tests/test_photo_qc_calibration.py`
  - `tests/test_photosets_intake_and_classification.py`
  - `tests/test_photo_derivatives_and_manifests.py`
- targeted frontend truth/UI proof passed:
  - `apps/web/tests/unit/CharacterImportIngest.test.tsx`
  - `apps/web/tests/unit/character-import.test.tsx`
- `make lint`: passed
- `make typecheck`: passed
