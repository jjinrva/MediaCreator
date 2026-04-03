# Phase 05 verify — generation proof-image runtime unblock

## Required checks

1. `generation-proof-image` job payload exists
2. generation request handling can queue the job in the ready case
3. the worker executes the job explicitly
4. ready runtime produces a real saved proof image artifact
5. blocked runtime does not fake output
6. placeholder workflow files do not satisfy generation `ready`
7. final verification docs are refreshed only after the real pass

## Mandatory evidence

### Code evidence
- line references for:
  - new job payload
  - queue helper
  - worker branch
  - provider execution service
  - tightened generation capability logic

### Runtime or test evidence
- blocked test output
- ready-path test output
- artifact existence proof
- lineage/storage proof

### Workflow truth evidence
- proof that placeholder `nodes: []` no longer count as ready
- proof that runnable validated workflows or explicit blocked state now exist

### Final truth evidence
- updated final verify report only if the phase actually passed
- updated overnight acceptance report only if the phase actually passed

## Required tests

At minimum, run targeted tests that prove:

- placeholder workflows keep generation blocked
- validated workflows can produce `ready`
- blocked proof-image request stores the request only
- ready proof-image path writes a real artifact
- request storage alone never counts as proof-image completion

## Stop rule

If the environment cannot produce a real proof image:
- write a blocker report
- keep the repo in a truthful blocked state
- do not start another scope
