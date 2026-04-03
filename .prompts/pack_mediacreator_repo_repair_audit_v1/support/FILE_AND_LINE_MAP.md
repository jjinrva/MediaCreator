# File and line map

Use these as the primary repair anchors.

## Status truth
- `PLANS.md:7-34`
- `README.md:75-84`
- `README.md:180-184`

## Photoset ingest
- `apps/api/app/api/routes/photosets.py:67-104`
- `apps/api/app/services/photo_prep.py:660-718`
- `apps/api/app/services/photo_prep.py:732-1110`
- `apps/api/app/services/jobs.py:47-54`
- `apps/api/app/services/jobs.py:492-650`

## Frontend intake progress and previews
- `apps/web/components/character-import/CharacterImportIngest.tsx:499-576`
- `apps/web/components/character-import/CharacterImportIngest.tsx:662-776`
- `apps/web/components/character-import/CharacterImportIngest.tsx:843-858`
- `apps/web/components/character-import/CharacterImportIngest.tsx:897-958`
- `apps/web/components/character-import/CharacterImportIngest.tsx:999-1077`

## QC logic and derivatives
- `apps/api/app/services/photo_prep.py:426-432`
- `apps/api/app/services/photo_prep.py:491-638`
- `apps/api/app/services/photo_prep.py:274-313`
- `apps/api/app/services/photo_prep.py:1026-1099`

## 3D / reconstruction truth
- `scripts/blender/rigify_proxy_export.py:60-175`
- `apps/api/app/services/reconstruction.py:104-121`
- `apps/api/app/services/reconstruction.py:176-202`
- `apps/api/app/services/reconstruction.py:220-253`
- `apps/api/app/services/reconstruction.py:330-376`
- `apps/api/app/services/exports.py:169-258`

## LoRA / generation / proof output
- `apps/api/app/services/lora_training.py:51-78`
- `apps/api/app/services/lora_training.py:295-333`
- `apps/api/app/services/lora_training.py:358-428`
- `apps/api/app/services/prompt_expansion.py:526-567`
- `apps/api/app/services/jobs.py:87-110`
- `apps/api/tests/test_lora_proof_image_contract.py:89-119`

## Existing tests that will need updates
- `apps/api/tests/test_photoset_job_progress.py:201-245`
- files that expect `photoset_response.status_code == 201`
