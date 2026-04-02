# Photo classification decision tree

This is the required intake routing contract for this pack.

## Rule 1 — person check happens first

For every uploaded image, ask:

1. is there a person in the image?
2. if not, reject it immediately with reason `no_person_detected`

Do not continue LoRA/body routing on non-person images.

## Rule 2 — evaluate LoRA and body suitability separately

After person presence is confirmed, compute and store at least these signals:

- `face_detected`
- `body_detected`
- `blur_score`
- `exposure_score`
- `framing_label`
- `occlusion_label`
- `resolution_ok`
- `has_person`

Then evaluate two separate boolean decisions:

- `usable_for_lora`
- `usable_for_body`

### LoRA suitability rules

An image may be `usable_for_lora` only if:

- `has_person == true`
- `face_detected == true`
- the image passes the stricter blur threshold
- the image passes the stricter exposure/occlusion rules
- the visible subject is not so cropped or obstructed that identity learning becomes unreliable

### Body suitability rules

An image may be `usable_for_body` if:

- `has_person == true`
- body evidence is strong enough from pose/body detection or framing
- the image passes the more permissive body blur threshold
- the image passes the body exposure rules
- the image is not so cropped that body shape/silhouette becomes unusable

## Rule 3 — bucket assignment is exclusive and visible

Assign exactly one of:

- `both` if `usable_for_lora == true` and `usable_for_body == true`
- `lora_only` if only LoRA is true
- `body_only` if only body is true
- `rejected` if neither is true

## Rule 4 — body-only no-face images are valid

A body shot must not be rejected solely because `face_detected == false`.

If the image has sufficient body evidence but lacks a usable face, it must become `body_only`.

## Rule 5 — different blur strictness

Use one stored blur metric and two thresholds:

- `min_blur_for_lora`
- `min_blur_for_body`

`min_blur_for_body` must be less strict than `min_blur_for_lora`.

The exact values must be documented in the phase report using the current implementation’s metric.
Do not use a single blur threshold for both purposes.

## Rule 6 — conservative preprocessing only

Do not “rescue” obviously bad images with aggressive edits.

Allowed:
- orientation normalization
- ICC/profile normalization to sRGB
- mild exposure/white-balance normalization
- body background removal derivative

Forbidden:
- beautification filters
- heavy denoise / heavy sharpen
- identity-changing retouch
- hallucinated face repair
- upscaling as a substitute for quality

## Rule 7 — reasons must be operator-readable

Each image record must include:

- bucket
- pass/warn/fail status if still used
- machine-readable reason codes
- operator-readable reason messages
