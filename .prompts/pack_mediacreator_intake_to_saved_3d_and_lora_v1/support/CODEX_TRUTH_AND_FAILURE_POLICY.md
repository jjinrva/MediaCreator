# Codex truth and failure policy

These are hard execution rules for this pack.

## Allowed status words

- `IMPLEMENTED_PENDING_VERIFY`
- `PASS`
- `FAIL`
- `BLOCKED`

Do not invent softer words that hide failure.

## Prohibited claims

Do not say any of the following unless the verify file proves it:

- complete
- done
- working
- generated
- saved
- ready
- trained
- fixed

## Required evidence before success language

### For UI claims
- Playwright or deterministic component/test proof

### For API claims
- TestClient or HTTP integration proof

### For file/artifact claims
- actual filesystem existence check
- corresponding database or registry record existence check

### For 3D output claims
- GLB file exists
- the output record exists
- the character detail page resolves it without fake placeholder language

### For LoRA claims
- trainer capability check passed
- model artifact exists
- model registry record exists
- a proof image generated from that artifact exists

## What to do on failure

- stop the phase
- write a blocker or fail report
- rerun only after repair
- never roll failure forward into later phases

## What to do when the runtime cannot support a required dependency

- capture the exact failing command
- capture the exact environment limitation
- mark the phase `BLOCKED`
- do not claim an emulated or mocked output is equivalent to the real output
