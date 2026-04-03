# Codex truth and failure policy

## Allowed phase result words

- `IMPLEMENTED_PENDING_VERIFY`
- `PASS`
- `FAIL`
- `BLOCKED`

Use nothing softer.

## Prohibited claims without verify proof

Do not say any of these unless the verify file proves them:

- fixed
- done
- working
- generated
- saved
- ready
- completed
- trained

## Required evidence before a PASS

### For docs/status fixes
- diff shows the claim was changed
- verify confirms the replacement language matches real code behavior

### For backend/API fixes
- deterministic API test passes
- route status code / payload matches contract
- worker path exists and is exercised

### For job execution fixes
- queued job exists
- worker claims it
- worker produces the expected output
- job status reaches completed only after artifact and record checks

### For UI fixes
- deterministic component/UI test or Playwright proof
- no placeholder language contradicts runtime truth

### For artifact claims
- file exists on disk
- storage object exists
- lineage or registry record exists

## What to do when verify fails

- stop the phase
- capture the exact failing command
- capture the changed files
- capture the failure summary
- write `reports/BLOCKER_REPORT_TEMPLATE.md` using the real failure
- do not continue

## What to do when runtime dependencies are missing

- mark the phase `BLOCKED`
- capture the missing dependency exactly
- do not replace the real dependency with a fake success path
