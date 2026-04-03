# Repo Repair Audit Phase 03 Verification

## Status

PASS

## Checks

1. a no-person image is rejected before LoRA/body routing
2. a clear face portrait with weak body evidence lands in `lora_only`
3. a body shot with no face but strong body evidence lands in `body_only`
4. a fully usable shot lands in `both`
5. a borderline body image is not rejected solely because no face is visible
6. persisted reason codes/messages and QC metric flags match the routing decision
7. derivative coverage still exists for the accepted buckets

## QC calibration evidence

Command:

```bash
rg -n "MIN_BLUR_FOR_BODY|_qc_metrics\\(|_qc_report_from_signals\\(|borderline but still acceptable for body modeling|person_detected|blur_ok_for_lora|blur_ok_for_body|exposure_ok_for_lora|exposure_ok_for_body" \
  /opt/MediaCreator/apps/api/app/services/photo_prep.py \
  /opt/MediaCreator/apps/api/app/schemas/photosets.py \
  /opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx
```

Result:

```text
/opt/MediaCreator/apps/api/app/services/photo_prep.py:57:MIN_BLUR_FOR_BODY = 55.0
/opt/MediaCreator/apps/api/app/services/photo_prep.py:433:def _qc_metrics(
/opt/MediaCreator/apps/api/app/services/photo_prep.py:443:    person_detected = face_detected or body_detected
/opt/MediaCreator/apps/api/app/services/photo_prep.py:444:    blur_ok_for_lora = blur_score >= MIN_BLUR_FOR_LORA
/opt/MediaCreator/apps/api/app/services/photo_prep.py:445:    blur_ok_for_body = blur_score >= MIN_BLUR_FOR_BODY
/opt/MediaCreator/apps/api/app/services/photo_prep.py:446:    exposure_ok_for_lora = MIN_EXPOSURE_FOR_LORA <= exposure_score <= MAX_EXPOSURE_FOR_LORA
/opt/MediaCreator/apps/api/app/services/photo_prep.py:447:    exposure_ok_for_body = MIN_EXPOSURE_FOR_BODY <= exposure_score <= MAX_EXPOSURE_FOR_BODY
/opt/MediaCreator/apps/api/app/services/photo_prep.py:532:def _qc_report_from_signals(
/opt/MediaCreator/apps/api/app/services/photo_prep.py:604:            "Image sharpness is borderline but still acceptable for body modeling."
/opt/MediaCreator/apps/api/app/services/photo_prep.py:628:            "Exposure is borderline but still acceptable for body modeling."
/opt/MediaCreator/apps/api/app/schemas/photosets.py:23:    person_detected: bool
/opt/MediaCreator/apps/api/app/schemas/photosets.py:28:    blur_ok_for_lora: bool
/opt/MediaCreator/apps/api/app/schemas/photosets.py:29:    blur_ok_for_body: bool
/opt/MediaCreator/apps/api/app/schemas/photosets.py:31:    exposure_ok_for_lora: bool
/opt/MediaCreator/apps/api/app/schemas/photosets.py:32:    exposure_ok_for_body: bool
/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx:41:    blur_ok_for_body: boolean;
/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx:42:    blur_ok_for_lora: boolean;
/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx:46:    exposure_ok_for_body: boolean;
/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx:47:    exposure_ok_for_lora: boolean;
/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx:52:    person_detected: boolean;
```

## Deterministic routing test evidence

Command:

```bash
cd /opt/MediaCreator/apps/api && .venv/bin/pytest -q \
  tests/test_photo_qc_calibration.py \
  tests/test_photosets_intake_and_classification.py \
  tests/test_photo_derivatives_and_manifests.py
```

Result:

```text
........                                                                 [100%]
8 passed in 6.15s
```

Supporting fixture coverage:

- [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py#L4) rejects no-person images first
- [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py#L16) routes clear face portraits with weak body evidence to `lora_only`
- [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py#L32) routes no-face body shots to `body_only`
- [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py#L54) routes fully usable shots to `both`
- [test_photo_qc_calibration.py](/opt/MediaCreator/apps/api/tests/test_photo_qc_calibration.py#L68) keeps borderline no-face body images in `body_only`

## Frontend truth evidence

Command:

```bash
cd /opt/MediaCreator/apps/web && ../../infra/bin/pnpm exec vitest run \
  tests/unit/CharacterImportIngest.test.tsx \
  tests/unit/character-import.test.tsx
```

Result:

```text
✓ tests/unit/CharacterImportIngest.test.tsx (2 tests)
✓ tests/unit/character-import.test.tsx (3 tests)

Test Files  2 passed (2)
Tests       5 passed (5)
```

## Repo safety checks

Commands:

```bash
make -C /opt/MediaCreator lint
make -C /opt/MediaCreator typecheck
```

Results:

- `make lint`: passed
- `make typecheck`: passed

## Artifact proof

- `tests/test_photosets_intake_and_classification.py` passed after asserting the persisted payload buckets and reason codes for `body_only`, `both`, and `rejected`
- `tests/test_photo_derivatives_and_manifests.py` passed after asserting accepted derivative artifacts and saved derivative manifests still exist for downstream body and LoRA use

## Conclusion

Phase 03 passes. QC routing now preserves person-first gating, keeps LoRA and body rules separate, allows body-only no-face acceptance when body evidence is strong enough, and persists the sub-check metrics needed for truthful frontend review.
