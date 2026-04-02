# Phase 24 build — Controlled video rendering from rigged characters

## Goal

Render simple character-controlled videos such as jumping up and down by applying motion to the rigged model and rendering the result, not by generating AI videos from scratch.

This phase is complete only when the user-visible and API-visible behavior for this phase is working, verified, and documented. Codex must follow **one chosen path** and may not substitute alternate frameworks or libraries without writing a blocker report first.

## Experts Codex must use for this phase

- `/experts/MOTION_AND_VIDEO_EXPERT.md`
- `/experts/BLENDER_RIGGING_AND_GLTF_EXPERT.md`
- `/experts/FASTAPI_DOMAIN_ARCHITECT.md`
- `/experts/QA_VERIFICATION_EXPERT.md`

Read those expert files before changing code. Do not treat them as optional.

## Chosen tools and libraries for this phase

- Blender background rendering
- job runner
- video output metadata

### Source IDs to use for this phase
S28, S30, S31, S43


## Exact chosen path for this phase

- Render character-controlled motion via rigged Blender animation.
- Do not substitute text-to-video or one-shot AI video generation for this requirement.


## Files and directories this phase is allowed to create or modify first

- apps/api/app/services/video_render.py
- workflows/blender/render_actions.py
- apps/web/app/studio/video

Codex should inspect adjacent files as needed, but it must begin with these areas and keep the change surface focused.

## Exact execution order

### Step 1
Create a video render job type that takes: character asset, current body state, current pose state, optional face state, selected action clip, and output resolution/duration.

### Step 2
Use Blender background rendering to produce the clip. The camera and scene can remain simple in this phase because full scenes are intentionally deferred. The key requirement is that the character motion is rig-driven.

### Step 3
Register the video output as an asset with lineage, storage metadata, and history. Surface the output in the UI with a truthful player or download link.

### Step 4
Do not substitute an AI text-to-video call here. The core requirement is controlled rig animation.


## Documentation Codex must update during this phase

- `docs/phase_reports/phase_24.md`
- any architecture doc created by this phase
- the root `README.md` if this phase changes setup or usage

## Deliverables for this phase

- video render job
- Blender render script
- output registration
- UI output view

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
4. `docs/phase_reports/phase_24.md` is updated with exact commands and results.
