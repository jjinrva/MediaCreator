# Patch matrix

| Priority | Area | Required patch |
|---|---|---|
| P0 | `jobs.py` | add `generation-proof-image` job payload |
| P0 | `jobs.py` | add worker execution branch for proof-image jobs |
| P0 | generation service | add queue helper and execution service |
| P0 | storage/lineage | persist proof-image artifact plus lineage to request and character |
| P0 | workflows | replace placeholders or keep capability blocked |
| P0 | capability logic | require real workflow validation, not just file presence |
| P0 | tests | add blocked and ready proof-image tests |
| P1 | UI/runtime detail | separate transfer progress from backend processing progress |
| P1 | docs/verify | refresh final verify/handoff docs after the real pass |
