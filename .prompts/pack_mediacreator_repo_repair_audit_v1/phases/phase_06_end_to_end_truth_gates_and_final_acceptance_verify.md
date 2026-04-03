# Phase 06 verify — end-to-end truth gates and final acceptance

## Required checks

- end-to-end acceptance path passes when runtime capabilities are actually present
- blocked capabilities are reported as blocked, not passed
- final report includes artifact paths and explicit truth statements
- no stale overclaim remains in docs, UI, or API payloads

## Final pass condition

Only pass if:
- all repaired contracts are verified
- all claimed artifacts exist
- no remaining overclaim is found in the audited surfaces
