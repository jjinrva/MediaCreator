"use client";

import { useRouter } from "next/navigation";
import React from "react";

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
  trainingJobStatus: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

export function LoraTrainingStatus({
  activeModel,
  capabilityDetail,
  capabilityStatus,
  characterPublicId,
  datasetStatus,
  missingRequirements,
  registry,
  trainingJobDetail,
  trainingJobStatus
}: LoraTrainingStatusProps) {
  const router = useRouter();
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isTraining, setIsTraining] = React.useState(false);
  const canTrain = capabilityStatus === "ready" && datasetStatus === "available";

  async function handleTrain() {
    try {
      setActionError(null);
      setActionSummary(null);
      setIsTraining(true);

      const response = await fetch(
        `${API_BASE_URL}/api/v1/lora/characters/${characterPublicId}`,
        { method: "POST" }
      );
      const payload = (await response.json()) as {
        detail?: string;
        training_job?: { detail: string; status: string };
      };

      if (!response.ok) {
        throw new Error(payload.detail ?? "LoRA training request failed.");
      }
      if (!payload.training_job) {
        throw new Error("LoRA training response was incomplete.");
      }
      if (payload.training_job.status !== "completed") {
        throw new Error(payload.training_job.detail);
      }

      setActionSummary(payload.training_job.detail);
      router.refresh();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "LoRA training failed before completion.";
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
          disabled={!canTrain || isTraining}
        >
          {isTraining ? "Running AI Toolkit..." : "Train LoRA locally"}
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
      </div>
    </div>
  );
}
