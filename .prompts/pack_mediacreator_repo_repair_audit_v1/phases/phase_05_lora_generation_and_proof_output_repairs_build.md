# Phase 05 build — LoRA generation and proof output repairs

## Goal

Repair the gap between “generation request stored” and “proof image actually generated”.

## Required changes

1. Keep the current readiness truth
   - if AI Toolkit or generation runtime is unavailable, do not claim generation output
   - preserve current conditional capability logic

2. Add a real generation execution path
   - introduce a job payload and worker execution branch for proof-image generation
   - only queue generation when runtime capability is `ready`
   - store the produced proof image as a real artifact with lineage to:
     - generation request
     - character
     - active local LoRA if used

3. Keep staged behavior when runtime is unavailable
   - request may be stored
   - proof image must remain absent
   - UI/API must say blocked or unavailable, not generated

4. Add artifact and lineage checks
   - proof image file exists
   - storage object exists
   - generation request resolves it
   - active LoRA registry entry resolves correctly

## Required tests

- unavailable runtime → generation request stored, no proof image artifact
- ready runtime → proof image job runs and a real artifact exists
- request storage alone never counts as proof output
