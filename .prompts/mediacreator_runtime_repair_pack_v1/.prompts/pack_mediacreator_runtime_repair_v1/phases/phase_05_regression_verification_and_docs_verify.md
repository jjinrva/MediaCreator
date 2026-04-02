# Phase 05 verify — regression verification and docs alignment

## Final command gates
Run, in a sensible order:
- backend lint
- backend typecheck
- backend targeted tests for photosets / characters / jobs / exports / system runtime
- web lint
- web typecheck
- web targeted unit tests
- web targeted Playwright tests

## Required scenarios
1. headless/LAN-safe runtime
2. upload/QC with accepted/rejected counts
3. zero-accepted character creation rejection
4. base-character build path
5. queued preview generation
6. progress polling
7. worker stale/offline visibility
8. terminal preview success or terminal failure state

## Final phase fails if
- any repaired flow still depends on a fixed LAN IP
- long-running routes are still synchronous
- the worker is still opaque to the operator
- the ingest-to-preview experience still feels like “nothing is happening”
