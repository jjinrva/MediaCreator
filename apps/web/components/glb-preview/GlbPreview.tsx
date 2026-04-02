"use client";

import React from "react";

import { JobProgressCard } from "../jobs/JobProgressCard";
import type { JobProgressSummary } from "../../lib/jobProgress";
import { isInFlightJobStatus } from "../../lib/jobProgress";
import { getApiBase } from "../../lib/runtimeApiBase";

type GlbPreviewProps = {
  alt: string;
  characterPublicId: string;
  detail: string;
  jobDetail: string;
  jobProgressPercent: number | null;
  jobPublicId: string | null;
  jobStatus: string;
  jobStepName: string | null;
  src: string | null;
  status: string;
  textureFidelity: string;
};


export function GlbPreview({
  alt,
  characterPublicId,
  detail,
  jobDetail,
  jobProgressPercent,
  jobPublicId,
  jobStatus,
  jobStepName,
  src,
  status,
  textureFidelity
}: GlbPreviewProps) {
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
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

  React.useEffect(() => {
    if (!src) {
      return;
    }

    void import("@google/model-viewer");
  }, [src]);

  async function handleGeneratePreview() {
    try {
      setActionError(null);
      setActionSummary(null);
      setIsGenerating(true);

      const response = await fetch(
        `${getApiBase()}/api/v1/exports/characters/${characterPublicId}/preview`,
        { method: "POST" }
      );
      if (!response.ok) {
        throw new Error("Preview export request failed.");
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
          : "Preview export failed before the queue request completed.";
      setActionError(message);
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div className="glbPreviewShell">
      <div className="glbPreviewViewport">
        {src ? (
          React.createElement("model-viewer", {
            alt,
            "camera-controls": true,
            className: "glbPreviewViewer",
            "data-testid": "glb-preview-viewer",
            exposure: "1",
            "interaction-prompt": "none",
            "shadow-intensity": "1",
            src
          })
        ) : (
          <div className="glbPreviewPlaceholder" role="status" aria-live="polite">
            <strong>No GLB preview is available yet.</strong>
            <p>{detail}</p>
          </div>
        )}
      </div>
      <div className="thumbnailMeta">
        <strong>Preview status</strong>
        <span className="thumbnailBadge">{status}</span>
        <span>{`Texture fidelity: ${textureFidelity}`}</span>
        <span>{detail}</span>
        <button
          type="button"
          className="previewActionButton"
          onClick={() => {
            void handleGeneratePreview();
          }}
          disabled={isGenerating || isJobInFlight}
        >
          {isGenerating
            ? "Queueing preview GLB..."
            : isJobInFlight
              ? "Preview job in progress..."
              : src
                ? "Regenerate preview GLB"
                : "Generate preview GLB"}
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
          <JobProgressCard initialJob={latestJob} title="Preview generation job" />
        ) : null}
      </div>
    </div>
  );
}
