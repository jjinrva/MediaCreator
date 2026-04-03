# Patch matrix

| Priority | Problem | Required repair | Primary files |
|---|---|---|---|
| P0 | All 26 phases marked PASS even though major gaps remain | Reset docs/status to truthful wording and current maturity | `PLANS.md`, `README.md`, `apps/api/app/services/exports.py` |
| P0 | Photoset ingest still runs inline in request | Split staging from worker execution; return `202` | `apps/api/app/api/routes/photosets.py`, `apps/api/app/services/photo_prep.py`, `apps/api/app/services/jobs.py` |
| P0 | Worker lacks real `photoset-ingest` executor | Add explicit branch and extract ingest execution path | `apps/api/app/services/jobs.py`, `apps/api/app/services/photo_prep.py`, `apps/worker/src/mediacreator_worker/main.py` |
| P0 | Proof-image generation not executed | Add real generation/proof-image job flow or truthful blocker flow | `apps/api/app/services/prompt_expansion.py`, `apps/api/app/services/jobs.py`, generation provider/workflow files |
| P1 | QC over-rejects some valid body shots | Calibrate routing and add better fallbacks/logging | `apps/api/app/services/photo_prep.py`, frontend intake detail UI/tests |
| P1 | 3D output stage is unclear | Distinguish proxy/base GLB from detail-prep and refined mesh | `apps/api/app/services/reconstruction.py`, `apps/api/app/services/exports.py`, character detail UI |
| P1 | Existing tests encode the wrong sync-ingest contract | Update tests to the async truth | `apps/api/tests/test_photoset_job_progress.py` and other tests expecting `201` |
| P2 | UI text around upload/server stages is confusing | Align button text, status cards, and summaries to async ingest flow | `apps/web/components/character-import/CharacterImportIngest.tsx` |
