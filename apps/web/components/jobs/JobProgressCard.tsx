"use client";

import { useRouter } from "next/navigation";
import React from "react";

import { getApiBase } from "../../lib/runtimeApiBase";
import type {
  JobDetailResponse,
  JobProgressSummary,
  WorkerHeartbeatResponse
} from "../../lib/jobProgress";
import { isTerminalJobStatus } from "../../lib/jobProgress";

type JobProgressCardProps = {
  initialJob: JobProgressSummary;
  title: string;
};

type JobSnapshot = {
  detail: string;
  errorSummary: string | null;
  jobPublicId: string;
  progressPercent: number | null;
  status: string;
  stepName: string | null;
};

type SystemStatusResponse = {
  worker: WorkerHeartbeatResponse;
};

function jobBadgeClassName(status: string): string {
  if (status === "completed") {
    return "thumbnailBadge thumbnailBadgePass";
  }
  if (status === "failed" || status === "canceled") {
    return "thumbnailBadge thumbnailBadgeFail";
  }
  return "thumbnailBadge thumbnailBadgeWarn";
}

function workerMessageClassName(workerStatus: string | null): string {
  return workerStatus === "ready" ? "previewActionSummary" : "previewActionError";
}

function stepLabel(stepName: string | null): string {
  return stepName ? stepName.replaceAll("-", " ") : "waiting for the worker";
}

function buildJobDetail(job: JobSnapshot): string {
  if (job.status === "failed") {
    return job.errorSummary ?? job.detail;
  }
  if (job.status === "completed") {
    return job.detail;
  }
  if (job.status === "canceled") {
    return "This job was canceled before it produced a final asset.";
  }
  return `Current step: ${stepLabel(job.stepName)}.`;
}

export function JobProgressCard({ initialJob, title }: JobProgressCardProps) {
  const router = useRouter();
  const [job, setJob] = React.useState<JobSnapshot | null>(
    initialJob.jobPublicId
      ? {
          detail: initialJob.detail,
          errorSummary: null,
          jobPublicId: initialJob.jobPublicId,
          progressPercent: initialJob.progressPercent,
          status: initialJob.status,
          stepName: initialJob.stepName
        }
      : null
  );
  const [worker, setWorker] = React.useState<WorkerHeartbeatResponse | null>(null);
  const [pollError, setPollError] = React.useState<string | null>(null);
  const [isRefreshing, startTransition] = React.useTransition();
  const refreshedTerminalStateRef = React.useRef(false);
  const activeJobDetail = job?.detail ?? initialJob.detail;
  const activeJobPublicId = job?.jobPublicId ?? null;
  const activeJobStatus = job?.status ?? null;

  React.useEffect(() => {
    if (!initialJob.jobPublicId) {
      setJob(null);
      setWorker(null);
      setPollError(null);
      refreshedTerminalStateRef.current = false;
      return;
    }

    setJob({
      detail: initialJob.detail,
      errorSummary: null,
      jobPublicId: initialJob.jobPublicId,
      progressPercent: initialJob.progressPercent,
      status: initialJob.status,
      stepName: initialJob.stepName
    });
    setWorker(null);
    setPollError(null);
    refreshedTerminalStateRef.current = isTerminalJobStatus(initialJob.status);
  }, [
    initialJob.detail,
    initialJob.jobPublicId,
    initialJob.progressPercent,
    initialJob.status,
    initialJob.stepName
  ]);

  React.useEffect(() => {
    if (!activeJobPublicId || !activeJobStatus || isTerminalJobStatus(activeJobStatus)) {
      return;
    }

    let cancelled = false;
    let timer: number | undefined;

    async function poll() {
      try {
        const [jobResponse, systemStatusResponse] = await Promise.all([
          fetch(`${getApiBase()}/api/v1/jobs/${activeJobPublicId}`, {
            cache: "no-store"
          }),
          fetch(`${getApiBase()}/api/v1/system/status`, {
            cache: "no-store"
          })
        ]);

        if (!jobResponse.ok) {
          throw new Error("Unable to refresh the queued job state.");
        }
        if (!systemStatusResponse.ok) {
          throw new Error("Unable to refresh the worker heartbeat.");
        }

        const jobPayload = (await jobResponse.json()) as JobDetailResponse;
        const systemStatusPayload = (await systemStatusResponse.json()) as SystemStatusResponse;

        if (cancelled) {
          return;
        }

        const nextJob: JobSnapshot = {
          detail:
            jobPayload.status === "failed"
              ? jobPayload.error_summary ?? activeJobDetail
              : jobPayload.status === "completed"
                ? initialJob.detail
                : activeJobDetail,
          errorSummary: jobPayload.error_summary,
          jobPublicId: jobPayload.public_id,
          progressPercent: jobPayload.progress_percent,
          status: jobPayload.status,
          stepName: jobPayload.step_name
        };

        setJob(nextJob);
        setWorker(systemStatusPayload.worker);
        setPollError(null);

        if (isTerminalJobStatus(nextJob.status)) {
          if (!refreshedTerminalStateRef.current) {
            refreshedTerminalStateRef.current = true;
            startTransition(() => router.refresh());
          }
          return;
        }

        timer = window.setTimeout(poll, 2000);
      } catch (error) {
        if (cancelled) {
          return;
        }

        setPollError(
          error instanceof Error
            ? error.message
            : "Unable to refresh the queued job state."
        );
        timer = window.setTimeout(poll, 2000);
      }
    }

    void poll();

    return () => {
      cancelled = true;
      if (timer !== undefined) {
        window.clearTimeout(timer);
      }
    };
  }, [activeJobDetail, activeJobPublicId, activeJobStatus, initialJob.detail, router]);

  if (!job) {
    return null;
  }

  const progressPercent = job.progressPercent ?? 0;
  const jobDetail = buildJobDetail(job);

  return (
    <div className="thumbnailCard jobProgressCard" role="status" aria-live="polite">
      <div className="jobProgressHeader">
        <strong>{title}</strong>
        <span className={jobBadgeClassName(job.status)}>{job.status}</span>
      </div>
      <div className="thumbnailMeta">
        <span>{jobDetail}</span>
        <span>{`Step: ${stepLabel(job.stepName)}`}</span>
        <span>{`Progress: ${progressPercent}%`}</span>
        <div
          className="jobProgressBar"
          aria-label={`${title} progress`}
          aria-valuemax={100}
          aria-valuemin={0}
          aria-valuenow={progressPercent}
          role="progressbar"
        >
          <div className="jobProgressBarFill" style={{ width: `${progressPercent}%` }} />
        </div>
        {worker ? (
          <span className={workerMessageClassName(worker.status)}>
            {worker.status === "ready"
              ? `Worker ready: ${worker.detail}`
              : `Worker ${worker.status}: ${worker.detail}`}
          </span>
        ) : null}
        {isRefreshing ? (
          <span className="previewActionSummary">Refreshing the page with the final resource state...</span>
        ) : null}
        {pollError ? (
          <span className="previewActionError" role="alert">
            {pollError}
          </span>
        ) : null}
      </div>
    </div>
  );
}
