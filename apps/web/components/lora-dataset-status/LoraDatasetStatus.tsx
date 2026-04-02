"use client";

import { useRouter } from "next/navigation";
import React from "react";

import { getApiBase } from "../../lib/runtimeApiBase";

type LoraDatasetStatusProps = {
  characterPublicId: string;
  detail: string;
  promptExpansion: string;
  promptHandle: string;
  status: string;
  visibleTags: string[];
};


export function LoraDatasetStatus({
  characterPublicId,
  detail,
  promptExpansion,
  promptHandle,
  status,
  visibleTags
}: LoraDatasetStatusProps) {
  const router = useRouter();
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isBuilding, setIsBuilding] = React.useState(false);

  async function handleBuildDataset() {
    try {
      setActionError(null);
      setActionSummary(null);
      setIsBuilding(true);

      const response = await fetch(
        `${getApiBase()}/api/v1/lora-datasets/characters/${characterPublicId}`,
        { method: "POST" }
      );
      if (!response.ok) {
        throw new Error("LoRA dataset request failed.");
      }

      const payload = (await response.json()) as {
        dataset: { detail: string; status: string };
      };
      if (payload.dataset.status !== "available") {
        throw new Error(payload.dataset.detail);
      }

      setActionSummary(payload.dataset.detail);
      router.refresh();
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "LoRA dataset build failed before the manifest became available.";
      setActionError(message);
    } finally {
      setIsBuilding(false);
    }
  }

  return (
    <div className="thumbnailCard reconstructionStatusCard">
      <div className="thumbnailMeta">
        <strong>Prompt handle contract</strong>
        <span className="thumbnailBadge">{status}</span>
        <span>{detail}</span>
        <span>{`Handle: ${promptHandle}`}</span>
        <span>{`Visible tags: ${visibleTags.join(", ")}`}</span>
        <pre className="promptAuditBlock">{promptExpansion}</pre>
        <button
          type="button"
          className="previewActionButton"
          onClick={() => {
            void handleBuildDataset();
          }}
          disabled={isBuilding}
        >
          {isBuilding
            ? "Building LoRA dataset..."
            : status === "available"
              ? "Rebuild LoRA dataset"
              : "Build LoRA dataset"}
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
