# Phase 05 verify — LoRA generation and proof output repairs

## Required checks

- generation/proof-image job payload exists
- worker executes it explicitly
- ready runtime produces a saved proof image artifact
- unavailable runtime does not fake output
- generation request storage alone does not satisfy proof-image acceptance

## Mandatory evidence

- test output for blocked case
- test output for real generation case
- artifact existence proof
- storage/registry lineage proof
