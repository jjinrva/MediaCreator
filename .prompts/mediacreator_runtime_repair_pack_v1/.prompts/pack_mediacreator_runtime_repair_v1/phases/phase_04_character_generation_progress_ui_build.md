# Phase 04 build — character generation progress UI

## Goal
Make the character workflow visibly progress from base creation to preview generation.

## Exact decisions
- After base character creation succeeds, immediately queue preview export.
- Redirect to the character detail route.
- Add one reusable `JobProgressCard` that polls `/api/v1/jobs/{job_public_id}` every 2 seconds while a job is non-terminal.
- On completion or failure, refresh the detail route and show the final resource state.
- Show worker-stale state clearly if the worker heartbeat is stale.

## Files to inspect and edit
- `apps/web/components/character-import/CharacterImportIngest.tsx`
- new `apps/web/components/jobs/JobProgressCard.tsx`
- `apps/web/app/studio/characters/[publicId]/page.tsx`
- `apps/web/components/glb-preview/GlbPreview.tsx`
- `apps/web/components/reconstruction-status/ReconstructionStatus.tsx`
- `apps/web/components/lora-training-status/LoraTrainingStatus.tsx`
- `apps/web/app/studio/video/VideoRenderPanel.tsx`
- any shared API-base helper added in phase 1
- unit/e2e tests

## Exact steps
1. Add a step indicator to the ingest page:
   - Upload photoset
   - Review QC
   - Build base character
   - Preview generation
2. After `POST /api/v1/characters` succeeds, immediately queue the preview export route.
3. Redirect to the character detail page.
4. On the detail page:
   - render `JobProgressCard` when the latest preview job is queued or running
   - render terminal success/failure state clearly
   - refresh the page when the job reaches a terminal state
5. Reuse the same progress card pattern for reconstruction, LoRA training, and video render surfaces where those payloads expose latest job IDs.
6. Fix `StudioFrame currentPath` on the character detail route.

## Required code patterns
Use:
- `CODE_EXAMPLES.md` section 5
- the route-queue pattern from phase 3
- the derived API-base helper from phase 1

## Do not do
- do not wait inside the UI for the whole long-running request
- do not use fake progress values
- do not leave the user without a clear “worker offline” or “job failed” message

## Done when
- the operator can upload, build a base character, land on the detail page, and watch preview generation progress
- the page updates honestly when the preview finishes or fails
