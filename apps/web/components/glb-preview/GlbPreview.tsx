"use client";

import { useRouter } from "next/navigation";
import React from "react";

type GlbPreviewProps = {
  alt: string;
  characterPublicId: string;
  detail: string;
  src: string | null;
  status: string;
  textureFidelity: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

export function GlbPreview({
  alt,
  characterPublicId,
  detail,
  src,
  status,
  textureFidelity
}: GlbPreviewProps) {
  const router = useRouter();
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);

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
        `${API_BASE_URL}/api/v1/exports/characters/${characterPublicId}/preview`,
        { method: "POST" }
      );
      if (!response.ok) {
        throw new Error("Preview export request failed.");
      }

      const payload = (await response.json()) as {
        export_job: { detail: string; status: string };
        preview_glb: { detail: string; status: string };
      };
      if (payload.preview_glb.status !== "available") {
        throw new Error(payload.export_job.detail);
      }

      setActionSummary(payload.export_job.detail);
      router.refresh();
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Preview export failed before the Blender runtime completed.";
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
          disabled={isGenerating}
        >
          {isGenerating
            ? "Generating preview GLB..."
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
      </div>
    </div>
  );
}
