# Gap report — should vs actual

## Should be true now

- proof-image generation can be queued and executed
- generation readiness cannot be satisfied by placeholder workflow contracts
- ready runtime produces a real saved image artifact
- blocked runtime remains truthful
- final verify and handoff reports reflect the latest real state

## Actual now

- generation requests are stored, but not executed
- there is no proof-image job kind
- there is no proof-image worker branch
- placeholder workflow files still exist
- tests still treat placeholder workflow files as enough for `generation ready`
- final verify and overnight acceptance docs are stale relative to the later Phase 05 stop
