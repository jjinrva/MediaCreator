"use client";

import React from "react";

import { JobProgressCard } from "../jobs/JobProgressCard";
import type { JobProgressSummary } from "../../lib/jobProgress";
import { isInFlightJobStatus } from "../../lib/jobProgress";
import { getApiBase } from "../../lib/runtimeApiBase";

type ReconstructionStatusProps = {
  characterPublicId: string;
  detail: string;
  detailLevel: string;
  jobDetail: string;
  jobProgressPercent: number | null;
  jobPublicId: string | null;
  jobStatus: string;
  jobStepName: string | null;
  strategy: string;
};


export function ReconstructionStatus({
  characterPublicId,
  detail,
  detailLevel,
  jobDetail,
  jobProgressPercent,
  jobPublicId,
  jobStatus,
  jobStepName,
  strategy
}: ReconstructionStatusProps) {
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isRunning, setIsRunning] = React.useState(false);
  const [queuedJob, setQueuedJob] = React.useState<JobProgressSummary | null>(null);

  const latestJob = queuedJob ?? {
    detail: jobDetail,
    jobPublicId,
    progressPercent: jobProgressPercent,
    status: jobStatus,
    stepName: jobStepName
  };
  const hasTrackedJob = latestJob.jobPublicId !== null && latestJob.status !== "not-queued";
  const isJobInFlight = isInFlightJobStatus(latestJob.status);

  async function handleRunReconstruction() {
    try {
      setActionError(null);
      setActionSummary(null);
      setIsRunning(true);

      const response = await fetch(
        `${getApiBase()}/api/v1/exports/characters/${characterPublicId}/reconstruction`,
        { method: "POST" }
      );
      if (!response.ok) {
        throw new Error("High-detail reconstruction request failed.");
      }

      const payload = (await response.json()) as {
        detail: string;
        job_public_id: string;
        progress_percent: number;
        status: string;
        step_name: string | null;
      };

      setQueuedJob({
        detail: payload.detail,
        jobPublicId: payload.job_public_id,
        progressPercent: payload.progress_percent,
        status: payload.status,
        stepName: payload.step_name
      });
      setActionSummary(payload.detail);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "High-detail reconstruction failed before the queue request completed.";
      setActionError(message);
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="thumbnailCard reconstructionStatusCard">
      <div className="thumbnailMeta">
        <strong>High-detail path</strong>
        <span className="thumbnailBadge">{detailLevel}</span>
        <span>{detail}</span>
        <span>{`Strategy: ${strategy}`}</span>
        <button
          type="button"
          className="previewActionButton"
          onClick={() => {
            void handleRunReconstruction();
          }}
          disabled={isRunning || isJobInFlight}
        >
          {isRunning
            ? "Queueing high-detail path..."
            : isJobInFlight
              ? "High-detail path in progress..."
              : latestJob.status === "completed"
              ? "Rerun high-detail path"
              : "Run high-detail path"}
        </button>
        {actionError ? (
          <span className="previewActionError" role="alert">
            {actionError}
          </span>
        ) : null}
        {actionSummary ? (
          <span className="previewActionSummary" role="status">
            {actionSummary}
          </span>
        ) : null}
        {hasTrackedJob ? (
          <JobProgressCard initialJob={latestJob} title="High-detail reconstruction job" />
        ) : null}
      </div>
    </div>
  );
}
