
# Postgres job dequeue pattern

Use one canonical dequeue query with `FOR UPDATE SKIP LOCKED`.

```sql
WITH picked AS (
  SELECT id
  FROM jobs
  WHERE state = 'queued'
  ORDER BY priority DESC, created_at ASC
  FOR UPDATE SKIP LOCKED
  LIMIT 1
)
UPDATE jobs
SET state = 'running',
    started_at = now()
WHERE id IN (SELECT id FROM picked)
RETURNING *;
```
