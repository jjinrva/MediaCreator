# Sources

## Repo evidence
- `scripts/run-api.sh`
- `scripts/run-web.sh`
- `.env.example`
- `apps/api/app/main.py`
- `apps/web/next.config.mjs`
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- `apps/api/app/api/routes/photosets.py`
- `apps/api/app/services/photo_prep.py`
- `apps/api/app/services/characters.py`
- `apps/api/app/services/jobs.py`
- `apps/api/app/api/routes/exports.py`
- `apps/api/app/api/routes/lora.py`
- `apps/api/app/api/routes/video.py`
- `apps/web/components/glb-preview/GlbPreview.tsx`
- `apps/web/components/reconstruction-status/ReconstructionStatus.tsx`
- `apps/web/components/lora-training-status/LoraTrainingStatus.tsx`
- `apps/web/app/studio/characters/[publicId]/page.tsx`

## Official docs used for implementation choices
- Uvicorn settings (`--host 0.0.0.0`)
- FastAPI request files / `UploadFile`
- Next.js CLI `next dev --hostname`
- `<model-viewer>` staging/camera/framing examples
