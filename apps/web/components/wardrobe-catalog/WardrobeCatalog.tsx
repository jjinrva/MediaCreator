/* eslint-disable @next/next/no-img-element */

"use client";

import { useRouter } from "next/navigation";
import React from "react";

import { getApiBase } from "../../lib/runtimeApiBase";

type WardrobeCatalogProps = {
  generationCapability: {
    detail: string;
    missingRequirements: string[];
    status: string;
  };
  items: Array<{
    baseColor: string;
    creationPath: string;
    fittingStatus: string;
    garmentType: string;
    history: Array<{
      createdAt: string;
      eventType: string;
      publicId: string;
    }>;
    label: string;
    material: string;
    promptText: string | null;
    publicId: string;
    sourcePhotoUrl: string | null;
    status: string;
  }>;
};


function defaultFormState() {
  return {
    baseColor: "",
    garmentType: "",
    label: "",
    material: ""
  };
}

export function WardrobeCatalog({ generationCapability, items }: WardrobeCatalogProps) {
  const router = useRouter();
  const [photoForm, setPhotoForm] = React.useState(defaultFormState);
  const [promptForm, setPromptForm] = React.useState({
    ...defaultFormState(),
    promptText: ""
  });
  const [photoFile, setPhotoFile] = React.useState<File | null>(null);
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isSubmittingPhoto, setIsSubmittingPhoto] = React.useState(false);
  const [isSubmittingPrompt, setIsSubmittingPrompt] = React.useState(false);

  function updatePhotoField(key: keyof typeof photoForm, value: string) {
    setPhotoForm((current) => ({ ...current, [key]: value }));
  }

  function updatePromptField(key: keyof typeof promptForm, value: string) {
    setPromptForm((current) => ({ ...current, [key]: value }));
  }

  async function submitPhotoForm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!photoFile) {
      setActionError("Select one garment photo before creating the wardrobe item.");
      return;
    }

    try {
      setActionError(null);
      setActionSummary(null);
      setIsSubmittingPhoto(true);

      const formData = new FormData();
      formData.append("photo", photoFile);
      formData.append("label", photoForm.label);
      formData.append("garment_type", photoForm.garmentType);
      formData.append("material", photoForm.material);
      formData.append("base_color", photoForm.baseColor);

      const response = await fetch(`${getApiBase()}/api/v1/wardrobe/from-photo`, {
        method: "POST",
        body: formData
      });
      const payload = (await response.json()) as { detail?: string; items?: unknown[] };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Wardrobe photo ingest failed.");
      }

      setActionSummary("Wardrobe item created from photo.");
      setPhotoForm(defaultFormState());
      setPhotoFile(null);
      router.refresh();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Wardrobe photo ingest failed.");
    } finally {
      setIsSubmittingPhoto(false);
    }
  }

  async function submitPromptForm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      setActionError(null);
      setActionSummary(null);
      setIsSubmittingPrompt(true);

      const response = await fetch(`${getApiBase()}/api/v1/wardrobe/from-prompt`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          base_color: promptForm.baseColor,
          garment_type: promptForm.garmentType,
          label: promptForm.label,
          material: promptForm.material,
          prompt_text: promptForm.promptText
        })
      });
      const payload = (await response.json()) as { detail?: string; items?: unknown[] };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Wardrobe prompt creation failed.");
      }

      setActionSummary("Prompt-backed wardrobe item created.");
      setPromptForm({
        ...defaultFormState(),
        promptText: ""
      });
      router.refresh();
    } catch (error) {
      setActionError(
        error instanceof Error ? error.message : "Wardrobe prompt creation failed."
      );
    } finally {
      setIsSubmittingPrompt(false);
    }
  }

  return (
    <div className="sectionCardBody">
      <div className="keyValueRow">
        <dt>AI wardrobe capability</dt>
        <dd>{generationCapability.status}</dd>
        <dd>{generationCapability.detail}</dd>
        <dd>
          {generationCapability.missingRequirements.length > 0
            ? `Missing requirements: ${generationCapability.missingRequirements.join(", ")}`
            : "Missing requirements: none"}
        </dd>
      </div>

      <div className="thumbnailGrid">
        <form className="thumbnailCard" onSubmit={(event) => void submitPhotoForm(event)}>
          <div className="thumbnailMeta fieldStack">
            <strong>Create from photo</strong>
            <label htmlFor="wardrobe-photo-file">Source photo</label>
            <input
              id="wardrobe-photo-file"
              className="textInput"
              type="file"
              accept="image/*"
              onChange={(event) => setPhotoFile(event.target.files?.[0] ?? null)}
              required
            />
            <label htmlFor="wardrobe-photo-label">Item label</label>
            <input
              id="wardrobe-photo-label"
              className="textInput"
              type="text"
              value={photoForm.label}
              onChange={(event) => updatePhotoField("label", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-photo-type">Garment type</label>
            <input
              id="wardrobe-photo-type"
              className="textInput"
              type="text"
              value={photoForm.garmentType}
              onChange={(event) => updatePhotoField("garmentType", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-photo-material">Material</label>
            <input
              id="wardrobe-photo-material"
              className="textInput"
              type="text"
              value={photoForm.material}
              onChange={(event) => updatePhotoField("material", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-photo-color">Base color</label>
            <input
              id="wardrobe-photo-color"
              className="textInput"
              type="text"
              value={photoForm.baseColor}
              onChange={(event) => updatePhotoField("baseColor", event.target.value)}
              required
            />
            <button type="submit" className="previewActionButton" disabled={isSubmittingPhoto}>
              {isSubmittingPhoto ? "Saving photo item..." : "Create wardrobe from photo"}
            </button>
          </div>
        </form>

        <form className="thumbnailCard" onSubmit={(event) => void submitPromptForm(event)}>
          <div className="thumbnailMeta fieldStack">
            <strong>Create from prompt</strong>
            <label htmlFor="wardrobe-prompt-label">Item label</label>
            <input
              id="wardrobe-prompt-label"
              className="textInput"
              type="text"
              value={promptForm.label}
              onChange={(event) => updatePromptField("label", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-prompt-type">Garment type</label>
            <input
              id="wardrobe-prompt-type"
              className="textInput"
              type="text"
              value={promptForm.garmentType}
              onChange={(event) => updatePromptField("garmentType", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-prompt-material">Material</label>
            <input
              id="wardrobe-prompt-material"
              className="textInput"
              type="text"
              value={promptForm.material}
              onChange={(event) => updatePromptField("material", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-prompt-color">Base color</label>
            <input
              id="wardrobe-prompt-color"
              className="textInput"
              type="text"
              value={promptForm.baseColor}
              onChange={(event) => updatePromptField("baseColor", event.target.value)}
              required
            />
            <label htmlFor="wardrobe-prompt-text">Prompt text</label>
            <textarea
              id="wardrobe-prompt-text"
              className="textInput"
              rows={4}
              value={promptForm.promptText}
              onChange={(event) => updatePromptField("promptText", event.target.value)}
              required
            />
            <button type="submit" className="previewActionButton" disabled={isSubmittingPrompt}>
              {isSubmittingPrompt ? "Saving prompt item..." : "Create wardrobe from prompt"}
            </button>
          </div>
        </form>
      </div>

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

      {items.length === 0 ? (
        <div className="keyValueRow">
          <dt>No wardrobe items yet</dt>
          <dd>Create the first closet item from a real photo or a prompt-backed request.</dd>
        </div>
      ) : (
        <div className="thumbnailGrid">
          {items.map((item) => (
            <article key={item.publicId} className="thumbnailCard">
              {item.sourcePhotoUrl ? (
                <img
                  className="thumbnailPreview"
                  src={item.sourcePhotoUrl}
                  alt={`Wardrobe source ${item.label}`}
                  width={240}
                  height={240}
                />
              ) : null}
              <div className="thumbnailMeta">
                <strong>{item.label}</strong>
                <span>{item.garmentType}</span>
                <span className="thumbnailBadge">{item.status}</span>
                <span>{`Material: ${item.material}`}</span>
                <span>{`Base color: ${item.baseColor}`}</span>
                <span>{`Fitting: ${item.fittingStatus}`}</span>
                <span>{`Created via: ${item.creationPath}`}</span>
                {item.promptText ? <pre className="promptAuditBlock">{item.promptText}</pre> : null}
                <span>{`History entries: ${item.history.length}`}</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
