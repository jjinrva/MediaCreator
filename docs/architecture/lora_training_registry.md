# LoRA Training Registry

Phase 21 adds the first local LoRA training contract without pretending the trainer exists when it does not.

## Readiness rules

- The only supported local trainer is AI Toolkit.
- Training is `ready` only when AI Toolkit is installed and the NAS-backed LoRA root is available.
- If either requirement is missing, the API and UI report `unavailable` and the training action stays disabled.

## Registry rules

- Every character-scoped LoRA registry entry lives in PostgreSQL in `models_registry`.
- The registry uses status values `working`, `current`, `failed`, and `archived`.
- Only one `current` LoRA is allowed per character at a time.
- Produced LoRA binaries live on NAS-backed storage and are referenced through `storage_objects`.

## Activation contract

- `GET /api/v1/lora/characters/{character_public_id}` returns the current capability state, latest job status, registry rows, and active LoRA artifact.
- Generation-side code resolves the active LoRA through `resolve_generation_lora_activation(...)`, which returns the current NAS path plus the prompt handle needed for deterministic activation.
- Failed training attempts are recorded truthfully in both job state and character history.
