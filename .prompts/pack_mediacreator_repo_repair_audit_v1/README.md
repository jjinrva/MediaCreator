# MediaCreator repo repair pack

## Purpose

This pack repairs the audited gaps in the repo snapshot identified on `2026-04-03`.

It is not a feature-idea pack. It is a **repair pack**.

Use it to bring the codebase from “truthful scaffold plus partial implementations” to “truthful, test-backed runtime behavior.”

## Audit basis

- archive: `MediaCreator-review-slim-20260402-235253.zip`
- snapshot identifier: `4c95e6c06107c90f35b802b1292b0e200157db26`

## What this pack fixes

1. false or premature completion claims
2. synchronous photoset ingest disguised as async progress
3. missing worker execution for `photoset-ingest`
4. QC/acceptance behavior that is too brittle for valid body shots
5. 3D output wording and status that do not distinguish proxy/base output from refined output
6. missing proof-image generation execution path

## What this pack preserves

Do not re-implement or break these already-correct behaviors:

- required character label
- duplicate labels allowed
- click-to-enlarge thumbnail inspection
- person-first intake logic
- background removal for body derivatives
- conservative LoRA derivative normalization
- conditional LoRA readiness truth checks

## Required outcome

After this pack:

- repo status and docs match reality
- `POST /api/v1/photosets` is honestly asynchronous
- the worker really executes `photoset-ingest`
- body-only images are not rejected solely for missing face evidence
- saved 3D output communicates its true stage
- proof images are either truly generated and saved or explicitly blocked
- Codex cannot claim a fix unless verify evidence exists
