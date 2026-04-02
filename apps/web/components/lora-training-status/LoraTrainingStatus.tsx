"use client";

import React from "react";

import { JobProgressCard } from "../jobs/JobProgressCard";
import type { JobProgressSummary } from "../../lib/jobProgress";
import { isInFlightJobStatus } from "../../lib/jobProgress";
import { getApiBase } from "../../lib/runtimeApiBase";

type LoraTrainingStatusProps = {
  activeModel:
    | {
        modelName: string;
        promptHandle: string;
        storagePath: string;
      }
    | null;
  capabilityDetail: string;
  capabilityStatus: string;
  characterPublicId: string;
  datasetStatus: string;
  missingRequirements: string[];
  registry: Array<{
    modelName: string;
    promptHandle: string;
    status: string;
  }>;
  trainingJobDetail: string;
  trainingJobProgressPercent: number | null;
  trainingJobPublicId: string | null;
  trainingJobStatus: string;
  trainingJobStepName: string | null;
};


export function LoraTrainingStatus({
  activeModel,
  capabilityDetail,
  capabilityStatus,
  characterPublicId,
  datasetStatus,
  missingRequirements,
  registry,
  trainingJobDetail,
  trainingJobProgressPercent,
  trainingJobPublicId,
  trainingJobStatus,
  trainingJobStepName
}: LoraTrainingStatusProps) {
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isTraining, setIsTraining] = React.useState(false);
  const [queuedJob, setQueuedJob] = React.useState<JobProgressSummary | null>(null);
  const canTrain = capabilityStatus === "ready" && datasetStatus === "available";
  const latestJob = queuedJob ?? {
    detail: trainingJobDetail,
    jobPublicId: trainingJobPublicId,
    progressPercent: trainingJobProgressPercent,
    status: trainingJobStatus,
    stepName: trainingJobStepName
  };
  const hasTrackedJob = latestJob.jobPublicId !== null && latestJob.status !== "not-queued";
  const isJobInFlight = isInFlightJobStatus(latestJob.status);

  async function handleTrain() {
    try {
      setActionError(null);
      setActionSummary(null);
      setIsTraining(true);

      const response = await fetch(
        `${getApiBase()}/api/v1/lora/characters/${characterPublicId}`,
        { method: "POST" }
      );
      const payload = (await response.json()) as {
        detail?: string;
        training_job?: {
          detail: string;
          job_public_id: string | null;
          progress_percent: number | null;
          status: string;
          step_name: string | null;
        };
      };

      if (!response.ok) {
        throw new Error(payload.detail ?? "LoRA training request failed.");
      }
      if (!payload.training_job || payload.training_job.job_public_id === null) {
        throw new Error("LoRA training response was incomplete.");
      }

      setQueuedJob({
        detail: payload.training_job.detail,
        jobPublicId: payload.training_job.job_public_id,
        progressPercent: payload.training_job.progress_percent,
        status: payload.training_job.status,
        stepName: payload.training_job.step_name
      });
      setActionSummary(payload.training_job.detail);
    } catch (error) {
      const message = error instanceof Error
        ? error.message
        : "LoRA training failed before the queue request completed.";
      setActionError(message);
    } finally {
      setIsTraining(false);
    }
  }

  const requirementSummary =
    missingRequirements.length > 0 ? missingRequirements.join(", ") : "none";
  const registrySummary =
    registry.length > 0
      ? registry.map((entry) => `${entry.status}:${entry.modelName}`).join(", ")
      : "none";

  return (
    <div className="thumbnailCard reconstructionStatusCard">
      <div className="thumbnailMeta">
        <strong>Local AI Toolkit training</strong>
        <span className="thumbnailBadge">{capabilityStatus}</span>
        <span>{capabilityDetail}</span>
        <span>{`Dataset gate: ${datasetStatus}`}</span>
        <span>{`Latest job: ${trainingJobStatus}`}</span>
        <span>{trainingJobDetail}</span>
        <span>{`Missing requirements: ${requirementSummary}`}</span>
        <span>{`Registry: ${registrySummary}`}</span>
        <span>
          {activeModel
            ? `Active LoRA: ${activeModel.modelName} via ${activeModel.promptHandle}`
            : "Active LoRA: none"}
        </span>
        {activeModel ? <pre className="promptAuditBlock">{activeModel.storagePath}</pre> : null}
        <button
          type="button"
          className="previewActionButton"
          onClick={() => {
            void handleTrain();
          }}
          disabled={!canTrain || isTraining || isJobInFlight}
        >
          {isTraining
            ? "Queueing AI Toolkit training..."
            : isJobInFlight
              ? "LoRA training in progress..."
              : "Train LoRA locally"}
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
          <JobProgressCard initialJob={latestJob} title="LoRA training job" />
        ) : null}
      </div>
    </div>
  );
}
