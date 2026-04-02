"use client";

import { useRouter } from "next/navigation";
import React from "react";

type ReconstructionStatusProps = {
  characterPublicId: string;
  detail: string;
  detailLevel: string;
  jobStatus: string;
  strategy: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

export function ReconstructionStatus({
  characterPublicId,
  detail,
  detailLevel,
  jobStatus,
  strategy
}: ReconstructionStatusProps) {
  const router = useRouter();
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isRunning, setIsRunning] = React.useState(false);

  async function handleRunReconstruction() {
    try {
      setActionError(null);
      setActionSummary(null);
      setIsRunning(true);

      const response = await fetch(
        `${API_BASE_URL}/api/v1/exports/characters/${characterPublicId}/reconstruction`,
        { method: "POST" }
      );
      if (!response.ok) {
        throw new Error("High-detail reconstruction request failed.");
      }

      const payload = (await response.json()) as {
        reconstruction: {
          reconstruction_job: { detail: string; status: string };
        };
      };
      if (payload.reconstruction.reconstruction_job.status !== "completed") {
        throw new Error(payload.reconstruction.reconstruction_job.detail);
      }

      setActionSummary(payload.reconstruction.reconstruction_job.detail);
      router.refresh();
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "High-detail reconstruction failed before the current stage completed.";
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
          disabled={isRunning}
        >
          {isRunning
            ? "Running high-detail path..."
            : jobStatus === "completed"
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
      </div>
    </div>
  );
}
