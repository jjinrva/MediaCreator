# Master run

## Hard goal

Repair the audited repo so that:

- docs/status are truthful,
- intake progress is real,
- the worker executes the job kinds the product depends on,
- photo acceptance and routing match the intended operator logic,
- 3D output stages are explicit and not overstated,
- proof-image generation is either real or blocked honestly,
- every completion claim is backed by deterministic verification.

## Non-negotiable rules

- Do not create option-based prompts.
- Do not claim a capability exists unless the code path, test path, and artifact checks all confirm it.
- Do not leave `PLANS.md` or `README.md` overstating repo maturity.
- Do not keep `POST /api/v1/photosets` synchronous while the UI and docs describe async behavior.
- Do not accept a body image into the LoRA bucket without LoRA-specific evidence.
- Do not reject a body image from body modeling solely because no face is visible.
- Do not say “fixed”, “done”, “working”, “generated”, “saved”, or “ready” without verify proof.
- Stop on verify failure. Write a blocker report if the runtime or missing stack prevents completion.

## Required first read

Read these before editing:

- `support/CURRENT_AUDIT_BASIS.md`
- `support/FILE_AND_LINE_MAP.md`
- `support/OUTPUT_TRUTH_CONTRACT.md`
- `support/ASYNC_INGEST_CONTRACT.md`
- `support/CODEX_TRUTH_AND_FAILURE_POLICY.md`
- `reports/GAP_REPORT_SHOULD_VS_ACTUAL.md`
- `reports/PATCH_MATRIX.md`

## Expected final state

1. `PLANS.md` and `README.md` stop overstating completion.
2. `POST /api/v1/photosets` returns `202` and a usable ingest job reference.
3. the worker contains a real `photoset-ingest` execution branch.
4. the frontend shows real server-side progress after browser transfer completes.
5. intake classification explicitly records person-present, LoRA-suitable, body-suitable, and rejection reasons.
6. saved 3D status distinguishes:
   - proxy/base GLB,
   - detail-prep,
   - refined mesh.
7. proof-image generation has a real job path and saved artifact when capability is ready.
8. deterministic tests prove the repaired behavior.

## Stop conditions

Stop and write a blocker report if any of these are true:

- the current repo files diverge so much from the audited snapshot that the file map is no longer usable
- runtime dependencies required for proof-image generation cannot be made operational
- the code can only be made to “look complete” by lying about missing artifacts or missing execution paths
