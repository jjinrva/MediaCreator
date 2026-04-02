# Phase 02 build — Frontend intake truth, label, and thumbnail preview

## Phase goal

Patch the operator-facing intake screen so it truthfully reflects the backend ingest flow and lets the operator inspect images before creating a saved character.

## Experts Codex must use for this phase

- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

## Exact chosen path

- Keep `/studio/characters/new` as the canonical intake route.
- Put the required character-label input at the top of the intake form.
- Use `react-dropzone` for file selection.
- Use `XMLHttpRequest` upload progress for transfer progress.
- Poll the backend ingest/job state for server-side progress after transfer starts.
- Add a thumbnail click-to-enlarge dialog using the existing design system primitives already in the web app. Use Radix Dialog if the repo already uses Radix patterns.
- Show the exact bucket and reason details returned by the API. Do not invent client-side QC.

## Exact stack and libraries

- Next.js App Router
- react-dropzone
- browser `XMLHttpRequest`
- existing fetch/polling helpers
- Playwright for UI proof

### Source IDs for this phase
S01, S02, S03, S05

## Exact file areas

Start with these files:

- `apps/web/app/studio/characters/new/page.tsx`
- `apps/web/components/character-import/CharacterImportIngest.tsx`

Inspect adjacent intake components only as needed.

## Ordered steps

### Step 1 — require the label in the UI

Add a required character label field.

Rules:
- disable upload start until the field is non-empty after trim
- do not show duplicate-label warnings
- show helper text that labels may repeat and IDs remain unique

**Verification immediately after Step 1**
- add a frontend test for disabled upload when the label is empty
- add a frontend test that a reused label is accepted by the form

### Step 2 — show truthful transfer progress

Replace any generic “uploading photoset” state with a progress panel that shows:

- file count selected
- bytes uploaded / total bytes
- upload percentage
- current server stage name once available

**Verification immediately after Step 2**
- add a component or e2e test that observes transfer progress text
- assert the generic one-line hanging state is gone

### Step 3 — show live scan/classification progress

Poll the ingest job until complete or failed.

Required visible fields:
- current stage name
- processed files / total files
- bucket counts
- last processed file name if the API exposes it
- clear error state on failure

Do not let the operator click “Create saved character” until the ingest job finishes and at least one accepted image exists.

**Verification immediately after Step 3**
- add a Playwright test that waits through the scan state and sees bucket counts appear
- assert the create button stays disabled until the backend marks ingest complete

### Step 4 — enlarge thumbnails on click

Make every thumbnail clickable.

The enlarged view must show:
- larger image
- bucket
- reason messages
- key QC booleans or labels
- close control and keyboard escape handling

**Verification immediately after Step 4**
- add a Playwright test that clicks a thumbnail, opens the dialog, and checks the larger image and bucket details

### Step 5 — present explicit acceptance summary

After ingest finishes, render a visible summary for:
- `lora_only`
- `body_only`
- `both`
- `rejected`

Do not merge `body_only` into rejection.

**Verification immediately after Step 5**
- add a UI assertion test that proves all visible summary buckets are distinct

## Pass/fail criteria

### PASS
- the UI requires a label but allows duplicates
- transfer and server progress are both visible
- thumbnails enlarge on click
- the create button respects accepted-count gating
- `body_only` is a first-class visible bucket

### FAIL
- upload can still hang on a generic message with no stage detail
- the dialog does not open from thumbnails
- duplicate labels are blocked in the UI
- `body_only` images are visually treated like rejects
- the operator can create a character before ingest is complete

## Deliverables

- patched intake screen
- progress panel
- thumbnail preview dialog
- acceptance summary UI
- targeted frontend and Playwright tests

## Forbidden scope

- do not add manual photo-editing tools
- do not add character detail page changes yet
- do not create fake client-side QC
- do not claim phase success without Playwright proof

## Documentation Codex must update in this phase

- `docs/phase_reports/intake_saved_outputs_phase_02.md`
- `docs/verification/intake_saved_outputs_phase_02_verify.md`

## Exit condition

The phase may stop only when the paired verify file can prove the operator sees truthful progress and enlarged-thumbnail inspection.
