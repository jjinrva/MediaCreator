# Final acceptance template

## Run identifier
Add date/time and branch/commit.

## Flow executed
Upload -> classify -> create character -> 3D output -> LoRA training -> proof image.

## Input set summary
- total images
- lora_only
- body_only
- both
- rejected

## Saved outputs
- character public ID
- GLB output path
- LoRA artifact path
- proof image path

## Truth checks
- no fake completion states
- all artifacts existed at verification time
- duplicate label accepted
- thumbnail enlarge worked
- body-only image accepted for body flow

## Final decision
PASS / FAIL / BLOCKED
