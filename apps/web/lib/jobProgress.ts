export type JobProgressSummary = {
  detail: string;
  jobPublicId: string | null;
  progressPercent: number | null;
  status: string;
  stepName: string | null;
};

export type JobDetailResponse = {
  error_summary: string | null;
  finished_at: string | null;
  job_type: string;
  output_asset_id: string | null;
  output_storage_object_id: string | null;
  progress:
    | {
        bucket_counts: Record<string, number> | null;
        processed_files: number | null;
        total_files: number | null;
      }
    | null;
  progress_percent: number;
  public_id: string;
  started_at: string | null;
  stage_history: Array<{
    bucket_counts: Record<string, number> | null;
    created_at: string;
    event_type: string;
    processed_files: number | null;
    progress_percent: number | null;
    status: string | null;
    step_name: string | null;
    total_files: number | null;
  }>;
  status: string;
  step_name: string | null;
};

export type WorkerHeartbeatResponse = {
  detail: string;
  last_seen_at: string | null;
  seconds_since_heartbeat: number | null;
  service_name: string;
  stale_after_seconds: number;
  status: string;
};

export function isTerminalJobStatus(status: string): boolean {
  return status === "completed" || status === "failed" || status === "canceled";
}

export function isInFlightJobStatus(status: string): boolean {
  return status === "queued" || status === "running";
}
