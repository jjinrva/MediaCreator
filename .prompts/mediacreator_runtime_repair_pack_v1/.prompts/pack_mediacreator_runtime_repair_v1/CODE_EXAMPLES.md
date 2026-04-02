# Code examples for this repair pack

These examples show the exact implementation style Codex should follow.

## 1. Queue-only route response

```python
# apps/api/app/schemas/jobs.py
class QueuedJobResponse(BaseModel):
    job_public_id: uuid.UUID
    status: str
    step_name: str | None
    progress_percent: int
    detail: str

# apps/api/app/api/routes/exports.py
@router.post(
    "/characters/{character_public_id}/preview",
    response_model=QueuedJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def queue_character_preview_glb(...):
    with db_session.begin():
        job = queue_character_preview_export(db_session, character_public_id)

    return QueuedJobResponse(
        job_public_id=job.public_id,
        status=job.status,
        step_name=job.step_name,
        progress_percent=job.progress_percent,
        detail="Preview export queued. Follow the job until it reaches a terminal state.",
    )
```

## 2. Accepted-entry filtering for character creation

```python
accepted_entries = [
    entry
    for entry in photoset_entries
    if entry.qc_status in {"pass", "warn"}
]
if not accepted_entries:
    raise ValueError("Photoset has no accepted entries for character creation.")

accepted_entry_public_ids = [str(entry.public_id) for entry in accepted_entries]
accepted_photo_asset_ids = [str(entry.photo_asset_id) for entry in accepted_entries]
```

## 3. Worker heartbeat write

```python
def heartbeat_worker(session: Session) -> None:
    upsert_service_heartbeat(
        session,
        service_name="worker",
        detail="polling",
    )

while not shutdown_requested.is_set():
    with session_factory() as session:
        with session.begin():
            heartbeat_worker(session)
    result = run_worker_once(session_factory)
    shutdown_requested.wait(timeout=poll_seconds)
```

## 4. Browser-safe API base helper

```ts
// apps/web/lib/runtimeApiBase.ts
export function getBrowserApiBase(): string {
  if (process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL;
  }
  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8010`;
  }
  return process.env.MEDIACREATOR_INTERNAL_API_BASE_URL ?? "http://127.0.0.1:8010";
}
```

## 5. Reusable job polling hook

```ts
function useJobProgress(jobPublicId: string | null, enabled: boolean) {
  const [job, setJob] = React.useState<JobDetail | null>(null);

  React.useEffect(() => {
    if (!jobPublicId || !enabled) return;

    let cancelled = false;
    let timer: number | undefined;

    async function poll() {
      const response = await fetch(`${getBrowserApiBase()}/api/v1/jobs/${jobPublicId}`, {
        cache: "no-store",
      });
      if (!response.ok) return;
      const payload = (await response.json()) as JobDetail;
      if (cancelled) return;
      setJob(payload);

      if (!["completed", "failed", "canceled"].includes(payload.status)) {
        timer = window.setTimeout(poll, 2000);
      }
    }

    void poll();
    return () => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    };
  }, [jobPublicId, enabled]);

  return job;
}
```

## 6. LAN-safe CORS configuration

```python
allowed_origins = [
    origin.strip()
    for origin in os.getenv("MEDIACREATOR_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
allow_origin_regex = os.getenv(
    "MEDIACREATOR_ALLOWED_ORIGIN_REGEX",
    r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.?\d*)(:\d+)?$",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
)
```

## 7. Ingest CTA flow

```ts
// After upload succeeds
setSubmissionSummary(
  `${uploaded.accepted_entry_count} accepted, ${uploaded.rejected_entry_count} rejected. ` +
  `Review QC, then build the base character.`
);

// After character creation succeeds
const previewResponse = await fetch(`${apiBase}/api/v1/exports/characters/${created.public_id}/preview`, {
  method: "POST",
});
router.push(`/studio/characters/${created.public_id}`);
```
