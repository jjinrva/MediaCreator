# Codex truth and failure policy

## Hard rules

1. Do not claim proof-image generation exists unless:
   - a job payload exists
   - a queue path exists
   - a worker execution branch exists
   - a real image artifact file is written
   - a storage object exists for that artifact
   - lineage back to the generation request is persisted

2. Do not claim `generation ready` based only on:
   - workflow file presence
   - placeholder JSON with `nodes: []`
   - a base URL string without a usable provider path

3. Do not update final verification or handoff reports unless:
   - the new verify step actually passed
   - the artifact proof exists
   - the blocked case still remains truthful

4. If runtime dependencies cannot be made operable:
   - stop
   - write a blocker report
   - leave the repo in a truthful blocked state

5. Do not break these already-correct areas:
   - required character label
   - duplicate labels allowed
   - queued photoset ingest
   - body-only routing without face
   - thumbnail click-to-enlarge
   - body background removal derivative
   - conservative LoRA derivative normalization
   - base/proxy 3D truth wording

## Required evidence language

Use `PASS` only when there is direct proof.
Use `BLOCKED` when the dependency is missing or placeholder.
Use `PARTIAL` only when a limited truthful subset exists.
