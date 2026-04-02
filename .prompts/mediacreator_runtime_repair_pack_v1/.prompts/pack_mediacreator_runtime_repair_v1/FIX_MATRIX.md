# Fix matrix

| Finding | Required fix | Primary files |
|---|---|---|
| Hardcoded `10.0.0.102` runtime assumptions | Replace runtime defaults with bind-safe and host-derived behavior; clean tests/docs | `.env.example`, `apps/api/app/main.py`, `apps/web/next.config.mjs`, all web files with API_BASE_URL constants, Playwright config, README |
| Inline long-job execution | Remove `run_worker_once()` from HTTP routes and return queued job payloads with `202 Accepted` | `apps/api/app/api/routes/exports.py`, `apps/api/app/api/routes/lora.py`, `apps/api/app/api/routes/video.py` |
| No worker liveness | Add service heartbeat table + worker heartbeat writes + system status exposure | new migration, worker main loop, new service helper, `system_runtime.py`, `/api/v1/system/status` |
| No progress UI | Add reusable polling progress card and surface latest job ids in resource payloads | `schemas/*`, `services/exports.py`, `services/lora_training.py`, `services/video_render.py`, character/video pages, new UI component |
| Failed QC images flow into characters | Filter accepted entries (`pass` / `warn`) and block zero-accepted character creation | `services/characters.py`, `schemas/photosets.py`, `services/photo_prep.py`, ingest UI |
| Weak ingest next-step UX | Add stepper, accepted/rejected counts, clear CTA, auto-queue preview after base creation | `CharacterImportIngest.tsx`, detail page, new progress card |
| Wrong route context on character detail | Set `StudioFrame` current path to the actual detail route | `apps/web/app/studio/characters/[publicId]/page.tsx` |
| Upload lacks explicit limits | Add max photoset count and size validation with clear API errors | `routes/photosets.py`, `services/photo_prep.py`, tests |
