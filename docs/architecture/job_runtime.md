# Job runtime

## Queue model

- Jobs live in PostgreSQL.
- Workers claim queued jobs with `FOR UPDATE SKIP LOCKED`.
- Route handlers stay read-only or delegate mutations to the job service layer.

## Canonical states

- `queued`
- `running`
- `failed`
- `completed`
- `canceled`

## Recorded fields

- `progress_percent`
- `step_name`
- `error_summary`
- `started_at`
- `finished_at`
- `output_asset_id`
- `output_storage_object_id`

## History contract

- Queue, run, progress, complete, fail, and cancel transitions write `history_events`.
- History events link back to `jobs.id` so later phases can show queue lineage in the UI.
