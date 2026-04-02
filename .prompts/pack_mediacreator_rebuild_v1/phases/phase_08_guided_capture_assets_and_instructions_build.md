# Phase 08 build — Guided capture assets and onboarding instructions

## Goal

Generate and ship the capture guidance that tells the user exactly how to photograph a person for the best LoRA and 3D results, including generic male/female reference assets rendered from Blender.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/HUMAN_CAPTURE_AND_QC_EXPERT.md`
- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FRONTEND_APP_ROUTER_AND_ACCESSIBILITY_EXPERT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Blender 4.5 LTS
- Rigify
- documentation assets

### Source IDs to use for this phase
S25, S26, S27, S29, S30, S31



## Files and directories this phase is allowed to create or modify first

- docs/capture_guides
- apps/web/app/studio/capture-guide
- scripts/blender

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Use Blender to generate a generic male body and a generic female body, both with neutral materials, no background, and clearly readable silhouettes. Also generate close-up head examples. These are onboarding assets, not runtime sample content for the main character library.

### Step 2
Render a capture-board set that shows at minimum: front body, left side, right side, back body, three-quarter views, face front, face left, face right, neutral expression, hairline visibility guidance, and arms-away-from-torso guidance.

### Step 3
Write an explicit instruction page in the app and a markdown guide in docs that states how many photos to take, how far the camera should be, how much overlap is needed, what lighting is acceptable, what clothes to wear, and what backgrounds to avoid.

### Step 4
Add a note that higher-detail 3D reconstruction phases may require significantly more photos than LoRA phases. The UI should communicate that clearly and up front.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_08.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- capture guide page
- rendered mannequin assets
- capture guide docs

## What Codex must not do in this phase


- Do not create parallel implementations of the same concept.
- Do not add auth or multi-user logic in this phase unless the phase explicitly says to create future-ready fields only.
- Do not seed runtime screens with demo/sample data.
- Do not change the chosen stack.
- Do not continue to the next phase until this phase passes verify.


## Exit condition for the build phase

The build phase may stop only when:
1. the phase deliverables exist,
2. the changed code is coherent,
3. the paired verify file has enough hooks to test the phase honestly,
4. `docs/phase_reports/phase_08.md` is updated with exact commands and results.
