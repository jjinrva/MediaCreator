# Runtime Repair Phase 04

## Status

Implemented. Paired verification not yet run in this report.

## Goal

Make character creation land on a truthful queued-preview flow, expose reusable job polling in the UI, and show worker state clearly while long-running jobs are in progress.

## Changes made

- added shared job-progress types in [jobProgress.ts](/opt/MediaCreator/apps/web/lib/jobProgress.ts)
- added reusable polling UI in [JobProgressCard.tsx](/opt/MediaCreator/apps/web/components/jobs/JobProgressCard.tsx)
  - polls `/api/v1/jobs/{job_public_id}` every 2 seconds while non-terminal
  - polls `/api/v1/system/status` alongside the job
  - refreshes the route when the job reaches a terminal state
  - shows worker `ready` vs `stale` / `offline` state explicitly
- updated [CharacterImportIngest.tsx](/opt/MediaCreator/apps/web/components/character-import/CharacterImportIngest.tsx)
  - added the fourth ingest step for preview generation
  - after base character creation, immediately queues preview export
  - redirects to the character detail route after the preview job is queued
- updated [page.tsx](/opt/MediaCreator/apps/web/app/studio/characters/[publicId]/page.tsx)
  - fixed `StudioFrame currentPath` to the real detail route
  - aligned local web types with phase-03 job metadata
  - passes latest job ids, step names, and progress values to the UI surfaces
- updated [GlbPreview.tsx](/opt/MediaCreator/apps/web/components/glb-preview/GlbPreview.tsx), [ReconstructionStatus.tsx](/opt/MediaCreator/apps/web/components/reconstruction-status/ReconstructionStatus.tsx), [LoraTrainingStatus.tsx](/opt/MediaCreator/apps/web/components/lora-training-status/LoraTrainingStatus.tsx), and [VideoRenderPanel.tsx](/opt/MediaCreator/apps/web/app/studio/video/VideoRenderPanel.tsx)
  - queue long-running POST requests instead of pretending they finish inline
  - render the shared progress card from queued/running/latest job metadata
  - disable duplicate submits while the current job is in flight
- updated [page.tsx](/opt/MediaCreator/apps/web/app/studio/video/page.tsx) to map the phase-03 video job metadata into the client panel
- added queue-progress styling in [globals.css](/opt/MediaCreator/apps/web/app/globals.css)
- fixed the runtime worker launcher in [run_worker.sh](/opt/MediaCreator/scripts/run_worker.sh)
  - the worker now runs from the API virtualenv so the long-running export/reconstruction/video code has the API-side runtime packages it imports
- updated web unit coverage in:
  - [character-import.test.tsx](/opt/MediaCreator/apps/web/tests/unit/character-import.test.tsx)
  - [glb-preview.test.tsx](/opt/MediaCreator/apps/web/tests/unit/glb-preview.test.tsx)
  - [reconstruction-status.test.tsx](/opt/MediaCreator/apps/web/tests/unit/reconstruction-status.test.tsx)
  - [lora-training-status.test.tsx](/opt/MediaCreator/apps/web/tests/unit/lora-training-status.test.tsx)
  - [video-render-panel.test.tsx](/opt/MediaCreator/apps/web/tests/unit/video-render-panel.test.tsx)
  - new [job-progress-card.test.tsx](/opt/MediaCreator/apps/web/tests/unit/job-progress-card.test.tsx)
- updated browser coverage in:
  - [character-creation.spec.ts](/opt/MediaCreator/apps/web/tests/e2e/character-creation.spec.ts)
  - [video-render.spec.ts](/opt/MediaCreator/apps/web/tests/e2e/video-render.spec.ts)
  - new [worker.ts](/opt/MediaCreator/apps/web/tests/e2e/helpers/worker.ts)

## Result

- after base character creation, the preview export is queued immediately and the operator lands on the detail route with truthful progress state
- preview, reconstruction, LoRA training, and controlled video render surfaces now share one polling card pattern
- the UI says clearly when the worker is stale or offline instead of implying hidden progress
- the runtime worker launcher now uses an environment that can actually import the long-running API pipelines

## Pre-verification evidence

- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH /opt/MediaCreator/infra/bin/pnpm exec tsc --noEmit` passed
- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH /opt/MediaCreator/infra/bin/pnpm exec vitest run tests/unit/character-import.test.tsx tests/unit/glb-preview.test.tsx tests/unit/reconstruction-status.test.tsx tests/unit/lora-training-status.test.tsx tests/unit/video-render-panel.test.tsx tests/unit/job-progress-card.test.tsx` passed with `10` tests
- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH PLAYWRIGHT_BROWSERS_PATH=/opt/MediaCreator/infra/playwright /opt/MediaCreator/infra/bin/pnpm exec playwright test tests/e2e/character-creation.spec.ts` passed
- `cd /opt/MediaCreator/apps/web && PATH=/opt/MediaCreator/infra/bin:$PATH PLAYWRIGHT_BROWSERS_PATH=/opt/MediaCreator/infra/playwright /opt/MediaCreator/infra/bin/pnpm exec playwright test tests/e2e/video-render.spec.ts` passed
