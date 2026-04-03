# Phase 06 build — end-to-end truth gates and final acceptance

## Goal

Make the whole operator journey deterministic and hard to fake.

## Required work

1. Add or update end-to-end acceptance tests covering:
   - labeled upload
   - async ingest
   - bucket classification
   - thumbnail inspection path
   - saved character creation
   - saved proxy/base GLB
   - LoRA dataset
   - LoRA training when ready
   - proof image when ready

2. Add explicit blocker behavior
   - if generation runtime is unavailable, final acceptance must say `BLOCKED`, not `PASS`

3. Add a final report
   - use the provided final acceptance template
   - include artifact paths and failing checks if blocked

4. Re-run docs/status truth after all repairs
   - do not leave stale optimistic wording behind
