# LoRA Dataset Contract

Phase 20 defines the first explicit LoRA training-set contract for MediaCreator.

## Dataset selection rules

The dataset service uses only the character’s accepted reference set.

Current rules:

- source images come from the prepared normalized photos, not raw uploads
- the dataset is versioned as `dataset-v1`
- the manifest records source entry IDs, source photo asset IDs, copied image files, and caption files
- one dataset root exists per character per dataset version under the NAS-backed LoRA storage tree

This keeps lineage back to the capture set explicit and auditable.

## Prompt-handle contract

The prompt contract is versioned separately as `prompt-contract-v1`.

Current fields:

- `prompt_handle` — `@character_<slug>`
- `visible_tags` — explicit tags shown in the UI
- `prompt_expansion` — the exact visible expansion string the app resolves from the handle

The UI shows the handle and expansion string directly so a user can audit the training prompt contract before later generation phases use it.

## AI Toolkit-compatible shape

The current dataset root contains:

- `images/` copied prepared images
- `captions/` one text file per copied image
- `dataset_manifest.json` with prompt contract and source lineage

This is compatible with the common image-plus-caption dataset layout expected by local LoRA tooling.

## Truthfulness limits

Phase 20 does not claim training is running yet.

It does claim:

- the dataset folder and manifest can be built
- the prompt-handle expansion is explicit and visible
- later training phases can consume the current dataset contract without guessing at captions or lineage
