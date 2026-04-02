# Phase 03 verify — async job execution and worker heartbeat

## Verify with code and commands

### API gates
For each long-running route:
- preview export
- reconstruction
- LoRA training
- video render

Confirm:
1. response status is `202`
2. response includes a job public ID
3. the HTTP request does not run the whole job inline
4. the job is initially queued
5. the worker later moves it to running/completed/failed

### Worker gates
- stop the worker and queue a job
- confirm the job stays queued
- confirm system status reports stale/offline worker
- start the worker
- confirm the job progresses

### Test gates
- job service tests
- route tests for 202 behavior
- system status diagnostics tests
- migration tests

## Phase fails if
- any long-running route still calls `run_worker_once()` inline
- worker heartbeat is absent
- queued jobs cannot be distinguished from running/completed jobs
