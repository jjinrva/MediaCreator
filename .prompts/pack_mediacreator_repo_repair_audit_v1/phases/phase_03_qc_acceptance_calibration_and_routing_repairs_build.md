# Phase 03 build — QC acceptance calibration and routing repairs

## Goal

Repair the acceptance logic so intake follows the intended operator questions:

1. Is there a person in the image?
2. If yes, is it good for LoRA?
3. If not good for LoRA, is it still good for body modeling?
4. If good for both, tag it as both.

## Required changes

1. Preserve person-first gating
   - reject only when no person is detected
   - do not let later checks override that initial truth

2. Preserve separate LoRA vs body criteria
   - face evidence is required for LoRA
   - body evidence is required for body modeling
   - a missing face alone must not kill a body-qualified image

3. Improve borderline handling
   - calibrate blur/exposure thresholds using tests that reflect the reported operator pain
   - add clearer reason codes and messages for borderline cases
   - record which exact sub-check failed:
     - person_detected
     - face_detected
     - body_detected
     - resolution_ok
     - blur_ok_for_lora
     - blur_ok_for_body
     - exposure_ok_for_lora
     - exposure_ok_for_body

4. Keep and verify derivatives
   - body derivative stays background-removed
   - LoRA derivative stays conservative in color/light normalization

5. Update frontend detail display if needed
   - show the bucket
   - show stable reason messages
   - do not hide body-only acceptance behind a face-only message

## Required tests

Add deterministic tests for at least:
- no-person image → rejected
- clear face portrait with weak body → `lora_only`
- body shot with no face but strong body evidence → `body_only`
- full usable shot → `both`
- borderline but acceptable body image does not become rejected solely due to missing face

## Do not do in this phase

- do not overfit thresholds to one fixture set
- do not downgrade LoRA quality rules just to increase pass counts
