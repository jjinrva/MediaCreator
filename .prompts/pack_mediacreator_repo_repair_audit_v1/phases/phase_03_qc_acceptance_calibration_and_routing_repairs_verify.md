# Phase 03 verify — QC acceptance calibration and routing repairs

## Required checks

- body-only no-face case lands in `body_only`, not `rejected`
- LoRA still requires face evidence
- clear usable photos are not mislabeled as blurry without evidence
- persisted reason codes/messages match the bucket decision
- derivative artifacts still exist for the right buckets

## Mandatory evidence

- deterministic QC tests
- sample payloads showing reason codes
- artifact existence proof for body and LoRA derivatives
