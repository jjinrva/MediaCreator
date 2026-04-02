"use client";

/* eslint-disable @next/next/no-img-element */

import { useRouter } from "next/navigation";
import React from "react";
import { useDropzone } from "react-dropzone";

import { EmptyState } from "../ui/EmptyState";
import { InfoTooltip } from "../ui/InfoTooltip";
import { SectionCard } from "../ui/SectionCard";
import type { FieldMetadata } from "../ui/field-metadata";

type StagedPhoto = {
  file: File;
  id: string;
  objectUrl: string;
};

type PersistedPhotosetEntry = {
  artifact_urls: {
    normalized: string;
    original: string;
    thumbnail: string;
  };
  original_filename: string;
  public_id: string;
  qc_metrics: {
    body_landmarks_detected: boolean;
    blur_score: number;
    exposure_score: number;
    face_detected: boolean;
    framing_label: string;
  };
  qc_reasons: string[];
  qc_status: "fail" | "pass" | "warn";
};

type PersistedPhotoset = {
  entry_count: number;
  entries: PersistedPhotosetEntry[];
  public_id: string;
  status: string;
};

type CreatedCharacter = {
  public_id: string;
};

const CHARACTER_LABEL_FIELD: FieldMetadata = {
  id: "character-label",
  label: "Character label",
  helpText:
    "Optional label stored with the uploaded photoset. When you create the base character record, the API reuses this label for the new character detail route."
};

const PHOTOSET_FIELD: FieldMetadata = {
  id: "photoset-files",
  label: "Photoset files",
  helpText:
    "Drop PNG, JPEG, or WEBP files here, or choose them from disk. After upload, FastAPI stores the prepared files and exposes the create-character action for the persisted photoset."
};

const ACCEPTED_IMAGE_TYPES = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"]
} as const;
const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://127.0.0.1:8010";

function buildPhotoId(file: File) {
  return `${file.name}-${file.size}-${file.lastModified}`;
}

function formatFileSize(sizeInBytes: number) {
  if (sizeInBytes < 1024 * 1024) {
    return `${(sizeInBytes / 1024).toFixed(1)} KB`;
  }

  return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FieldHeader({ field }: { field: FieldMetadata }) {
  return (
    <div className="fieldHeader">
      <label htmlFor={field.id} className="fieldLabel">
        {field.label}
      </label>
      <InfoTooltip content={field.helpText} label={field.label} />
    </div>
  );
}

export function CharacterImportIngest() {
  const router = useRouter();
  const [characterLabel, setCharacterLabel] = React.useState("");
  const [photos, setPhotos] = React.useState<StagedPhoto[]>([]);
  const [currentPhotosetId, setCurrentPhotosetId] = React.useState<string | null>(null);
  const [persistedPhotoset, setPersistedPhotoset] = React.useState<PersistedPhotoset | null>(null);
  const [isLoadingPersisted, setIsLoadingPersisted] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isCreatingCharacter, setIsCreatingCharacter] = React.useState(false);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [submissionSummary, setSubmissionSummary] = React.useState<string | null>(null);
  const photosRef = React.useRef<StagedPhoto[]>([]);

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setCurrentPhotosetId(params.get("photoset"));
  }, []);

  React.useEffect(() => {
    photosRef.current = photos;
  }, [photos]);

  React.useEffect(() => {
    return () => {
      photosRef.current.forEach((photo) => URL.revokeObjectURL(photo.objectUrl));
    };
  }, []);

  React.useEffect(() => {
    if (!currentPhotosetId) {
      setPersistedPhotoset(null);
      return;
    }

    const controller = new AbortController();

    async function loadPhotoset() {
      setIsLoadingPersisted(true);
      setLoadError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/photosets/${currentPhotosetId}`, {
          signal: controller.signal
        });

        if (!response.ok) {
          throw new Error("Unable to load the uploaded photoset.");
        }

        const payload = (await response.json()) as PersistedPhotoset;
        setPersistedPhotoset(payload);
      } catch (error) {
        if ((error as Error).name === "AbortError") {
          return;
        }

        setLoadError("Unable to load the saved QC results.");
      } finally {
        setIsLoadingPersisted(false);
      }
    }

    void loadPhotoset();

    return () => controller.abort();
  }, [currentPhotosetId]);

  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    if (currentPhotosetId) {
      window.history.replaceState({}, "", "/studio/characters/new");
      setCurrentPhotosetId(null);
      setPersistedPhotoset(null);
    }

    setPhotos((currentPhotos) => {
      const existingIds = new Set(currentPhotos.map((photo) => photo.id));
      const nextPhotos = [...currentPhotos];

      acceptedFiles.forEach((file) => {
        const id = buildPhotoId(file);

        if (existingIds.has(id)) {
          return;
        }

        existingIds.add(id);
        nextPhotos.push({
          file,
          id,
          objectUrl: URL.createObjectURL(file)
        });
      });

      return nextPhotos;
    });
    setLoadError(null);
    setSubmissionSummary(null);
    setIsCreatingCharacter(false);
  }, [currentPhotosetId]);

  const { getInputProps, getRootProps, isDragActive, open } = useDropzone({
    accept: ACCEPTED_IMAGE_TYPES,
    multiple: true,
    noClick: true,
    onDrop
  });

  function removePhoto(photoId: string) {
    setPhotos((currentPhotos) => {
      const target = currentPhotos.find((photo) => photo.id === photoId);

      if (target) {
        URL.revokeObjectURL(target.objectUrl);
      }

      return currentPhotos.filter((photo) => photo.id !== photoId);
    });
    setLoadError(null);
    setSubmissionSummary(null);
    setIsCreatingCharacter(false);
  }

  function clearPhotos() {
    photos.forEach((photo) => URL.revokeObjectURL(photo.objectUrl));
    setPhotos([]);
    setLoadError(null);
    setSubmissionSummary(null);
    setIsCreatingCharacter(false);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const payload = new FormData();

    if (characterLabel.trim()) {
      payload.set("character_label", characterLabel.trim());
    }

    photos.forEach((photo) => {
      payload.append("photos", photo.file, photo.file.name);
    });

    try {
      setIsSubmitting(true);
      setLoadError(null);
      setIsCreatingCharacter(false);
      const response = await fetch(`${API_BASE_URL}/api/v1/photosets`, {
        body: payload,
        method: "POST"
      });

      if (!response.ok) {
        throw new Error("Photoset upload failed.");
      }

      const uploadedPhotoset = (await response.json()) as PersistedPhotoset;

      photos.forEach((photo) => URL.revokeObjectURL(photo.objectUrl));
      setPhotos([]);
      setPersistedPhotoset(uploadedPhotoset);
      setCurrentPhotosetId(uploadedPhotoset.public_id);
      setSubmissionSummary(
        `${uploadedPhotoset.entry_count} photo(s) uploaded. QC results are now loaded from the API and survive reload.`
      );
      window.history.replaceState(
        {},
        "",
        `/studio/characters/new?photoset=${uploadedPhotoset.public_id}`
      );
    } catch {
      setLoadError("Upload failed before the QC pipeline could return stable results.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCreateCharacter() {
    if (!persistedPhotoset) {
      return;
    }

    try {
      setIsCreatingCharacter(true);
      setLoadError(null);
      const response = await fetch(`${API_BASE_URL}/api/v1/characters`, {
        body: JSON.stringify({ photoset_public_id: persistedPhotoset.public_id }),
        headers: {
          "content-type": "application/json"
        },
        method: "POST"
      });

      if (!response.ok) {
        throw new Error("Character creation failed.");
      }

      const createdCharacter = (await response.json()) as CreatedCharacter;
      router.push(`/studio/characters/${createdCharacter.public_id}`);
    } catch {
      setLoadError("Base character creation failed before the detail route could load.");
      setIsCreatingCharacter(false);
    }
  }

  function badgeClassName(status: "fail" | "pass" | "warn") {
    if (status === "pass") {
      return "thumbnailBadge thumbnailBadgePass";
    }
    if (status === "warn") {
      return "thumbnailBadge thumbnailBadgeWarn";
    }
    return "thumbnailBadge thumbnailBadgeFail";
  }

  return (
    <div className="characterImportMain">
      <SectionCard
        title="Base character setup"
        description="Phase 11 uploads a photoset, stores QC-backed prepared references, and creates exactly one base character record from that persisted submission."
      >
        <form className="characterImportForm" onSubmit={handleSubmit}>
          <div className="fieldStack">
            <FieldHeader field={CHARACTER_LABEL_FIELD} />
            <input
              id={CHARACTER_LABEL_FIELD.id}
              className="textInput"
              type="text"
              value={characterLabel}
              onChange={(event) => {
                setCharacterLabel(event.target.value);
                setSubmissionSummary(null);
              }}
              placeholder="Optional local character label"
            />
          </div>

          <div className="fieldStack">
            <FieldHeader field={PHOTOSET_FIELD} />
            <div
              {...getRootProps({
                "aria-label": "Photoset dropzone",
                className: isDragActive ? "dropzoneSurface dropzoneSurfaceActive" : "dropzoneSurface",
                "data-testid": "ingest-dropzone"
              })}
            >
              <input
                {...getInputProps({
                  "aria-label": "Photoset files",
                  "data-testid": "photoset-input",
                  id: PHOTOSET_FIELD.id
                })}
              />
              <strong>{isDragActive ? "Drop photos here" : "Drag and drop photos here"}</strong>
              <p>
                Click the button if you prefer file selection. Supported formats: PNG, JPEG, and WEBP.
              </p>
              <div className="dropzoneActions">
                <button type="button" className="primaryLink" onClick={open}>
                  Choose photos
                </button>
                {photos.length > 0 ? (
                  <button type="button" className="themeToggle" onClick={clearPhotos}>
                    Clear all
                  </button>
                ) : null}
              </div>
            </div>
          </div>

          <div className="characterImportActionRow">
            <span className="secondaryNote">
              {photos.length === 0
                ? "No photos selected yet."
                : `${photos.length} photo(s) staged locally. QC stays neutral until the upload finishes.`}
            </span>
            <button
              type="submit"
              className="themeToggle"
              disabled={photos.length === 0 || isSubmitting}
            >
              {isSubmitting ? "Uploading photoset" : "Upload photoset"}
            </button>
          </div>

          {loadError ? (
            <p className="captureGuideAlert" role="alert">
              {loadError}
            </p>
          ) : null}

          {submissionSummary ? (
            <p className="characterImportSummary" role="status">
              {submissionSummary}
            </p>
          ) : null}
        </form>
      </SectionCard>

      <SectionCard
        title="Selected photos"
        description="Before submit, previews are browser-local object URLs. After submit, the grid reloads stored QC results from the API and can be promoted into the base character registry."
      >
        {photos.length > 0 ? (
          <div className="thumbnailGrid" data-testid="thumbnail-grid">
            {photos.map((photo) => (
              <article key={photo.id} className="thumbnailCard" data-testid="thumbnail-card">
                <img
                  className="thumbnailPreview"
                  src={photo.objectUrl}
                  alt={`Preview of ${photo.file.name}`}
                  width={240}
                  height={240}
                />
                <div className="thumbnailMeta">
                  <strong>{photo.file.name}</strong>
                  <span>{formatFileSize(photo.file.size)}</span>
                  <span className="thumbnailBadge">QC pending backend upload</span>
                </div>
                <button
                  type="button"
                  className="themeToggle"
                  onClick={() => removePhoto(photo.id)}
                  aria-label={`Remove ${photo.file.name}`}
                >
                  Remove
                </button>
              </article>
            ))}
          </div>
        ) : persistedPhotoset ? (
          <div className="thumbnailGrid" data-testid="thumbnail-grid">
            {persistedPhotoset.entries.map((entry) => (
              <article key={entry.public_id} className="thumbnailCard" data-testid="thumbnail-card">
                <img
                  className="thumbnailPreview"
                  src={entry.artifact_urls.thumbnail}
                  alt={`Prepared thumbnail of ${entry.original_filename}`}
                  width={240}
                  height={240}
                />
                <div className="thumbnailMeta">
                  <strong>{entry.original_filename}</strong>
                  <span>{entry.qc_metrics.framing_label}</span>
                  <span className={badgeClassName(entry.qc_status)}>
                    {`QC ${entry.qc_status}`}
                  </span>
                </div>
                <ul className="thumbnailReasonList">
                  {entry.qc_reasons.length > 0 ? (
                    entry.qc_reasons.map((reason) => <li key={reason}>{reason}</li>)
                  ) : (
                    <li>No issues detected.</li>
                  )}
                </ul>
              </article>
            ))}
          </div>
        ) : isLoadingPersisted ? (
          <EmptyState
            title="Loading saved QC results"
            description="The ingest page is reloading the stored photoset and its backend-generated QC state."
          />
        ) : (
          <EmptyState
            title="No photos staged yet"
            description="Add a photoset to generate local thumbnails and inspect the pending-backend QC placeholders."
          />
        )}

        <p className="secondaryNote">
          No previously created characters are shown here. This page only shows files chosen in the current browser session or the photoset identified in the current URL.
        </p>

        {persistedPhotoset ? (
          <div className="characterImportActionRow">
            <span className="secondaryNote">
              The current photoset is persisted. Creating the base character writes a single
              character asset, links it back to this photoset, and redirects to the API-backed
              detail page.
            </span>
            <button
              type="button"
              className="themeToggle"
              onClick={handleCreateCharacter}
              disabled={isLoadingPersisted || isCreatingCharacter}
            >
              {isCreatingCharacter ? "Opening base character" : "Create base character"}
            </button>
          </div>
        ) : null}
      </SectionCard>
    </div>
  );
}
