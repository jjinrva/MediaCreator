"use client";

/* eslint-disable @next/next/no-img-element */

import { useRouter } from "next/navigation";
import React from "react";
import { useDropzone } from "react-dropzone";

import type { JobDetailResponse } from "../../lib/jobProgress";
import { getApiBase } from "../../lib/runtimeApiBase";
import { EmptyState } from "../ui/EmptyState";
import { InfoTooltip } from "../ui/InfoTooltip";
import { SectionCard } from "../ui/SectionCard";
import type { FieldMetadata } from "../ui/field-metadata";

type BucketName = "lora_only" | "body_only" | "both" | "rejected";

type BucketCounts = Record<BucketName, number>;

type UploadPhase = "idle" | "uploading" | "server" | "complete" | "failed";

type StagedPhoto = {
  file: File;
  id: string;
  objectUrl: string;
};

type PersistedPhotosetEntry = {
  accepted_for_character_use: boolean;
  artifact_urls: {
    normalized: string;
    original: string;
    thumbnail: string;
  };
  bucket: BucketName;
  original_filename: string;
  photo_asset_public_id: string;
  public_id: string;
  qc_metrics: {
    blur_score: number;
    blur_ok_for_body: boolean;
    blur_ok_for_lora: boolean;
    body_detected: boolean;
    body_landmarks_detected: boolean;
    exposure_score: number;
    exposure_ok_for_body: boolean;
    exposure_ok_for_lora: boolean;
    face_detected: boolean;
    framing_label: string;
    has_person: boolean;
    occlusion_label: string;
    person_detected: boolean;
    resolution_ok: boolean;
  };
  qc_reasons: string[];
  qc_status: "fail" | "pass" | "warn";
  reason_codes: string[];
  reason_messages: string[];
  usable_for_body: boolean;
  usable_for_lora: boolean;
};

type IngestJobSummary = {
  bucket_counts: BucketCounts | null;
  job_public_id: string;
  processed_files: number | null;
  progress_percent: number;
  status: string;
  step_name: string | null;
  total_files: number | null;
};

type PersistedPhotoset = {
  accepted_entry_count: number;
  asset_type?: string;
  bucket_counts: BucketCounts;
  character_label: string | null;
  entries: PersistedPhotosetEntry[];
  entry_count: number;
  ingest_job: IngestJobSummary | null;
  public_id: string;
  rejected_entry_count: number;
  status: string;
};

type CreatedCharacter = {
  public_id: string;
};

type QueuedJobResponse = {
  detail?: string;
  job_public_id: string;
  progress_percent: number;
  status: string;
  step_name: string | null;
};

type IngestJobDetail = {
  bucketCounts: BucketCounts | null;
  errorSummary: string | null;
  jobPublicId: string;
  processedFiles: number | null;
  progressPercent: number;
  stageHistory: Array<{
    bucketCounts: BucketCounts | null;
    createdAt: string;
    eventType: string;
    processedFiles: number | null;
    progressPercent: number | null;
    status: string | null;
    stepName: string | null;
    totalFiles: number | null;
  }>;
  status: string;
  stepName: string | null;
  totalFiles: number | null;
};

type UploadProgressState = {
  bytesUploaded: number;
  phase: UploadPhase;
  percent: number;
  totalBytes: number;
};

type PreviewDialogState = {
  bucket: string;
  details: Array<{ label: string; value: string }>;
  imageUrl: string;
  reasonMessages: string[];
  title: string;
};

const EMPTY_BUCKET_COUNTS: BucketCounts = {
  lora_only: 0,
  body_only: 0,
  both: 0,
  rejected: 0
};

const CHARACTER_LABEL_FIELD: FieldMetadata = {
  id: "character-label",
  label: "Character label",
  helpText:
    "Required operator label for this intake run. Labels may repeat; the saved IDs stay unique."
};

const PHOTOSET_FIELD: FieldMetadata = {
  id: "photoset-files",
  label: "Photoset files",
  helpText:
    "Drop PNG, JPEG, or WEBP files here. Transfer progress comes from the browser upload, and bucket/reason data comes from the backend ingest record."
};

const ACCEPTED_IMAGE_TYPES = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"]
} as const;

function buildPhotoId(file: File) {
  return `${file.name}-${file.size}-${file.lastModified}`;
}

function formatBucketLabel(bucket: BucketName) {
  return bucket.replaceAll("_", " ");
}

function formatFileSize(sizeInBytes: number) {
  if (sizeInBytes <= 0) {
    return "0 KB";
  }
  if (sizeInBytes < 1024 * 1024) {
    return `${(sizeInBytes / 1024).toFixed(1)} KB`;
  }

  return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatStageLabel(stepName: string | null) {
  if (!stepName) {
    return "waiting for the backend ingest job";
  }
  return stepName.replaceAll(/[_-]/g, " ");
}

function bucketCountValue(bucketCounts: BucketCounts | null | undefined, bucket: BucketName) {
  if (!bucketCounts) {
    return 0;
  }
  return bucketCounts[bucket] ?? 0;
}

function normalizeBucketCounts(
  bucketCounts: Record<string, number> | BucketCounts | null | undefined
): BucketCounts | null {
  if (!bucketCounts) {
    return null;
  }

  return {
    body_only: bucketCounts.body_only ?? 0,
    both: bucketCounts.both ?? 0,
    lora_only: bucketCounts.lora_only ?? 0,
    rejected: bucketCounts.rejected ?? 0
  };
}

function isTerminalJobStatus(status: string | null | undefined) {
  return status === "completed" || status === "failed" || status === "canceled";
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

function bucketBadgeClassName(bucket: BucketName) {
  if (bucket === "both") {
    return "thumbnailBadge thumbnailBadgePass";
  }
  if (bucket === "rejected") {
    return "thumbnailBadge thumbnailBadgeFail";
  }
  return "thumbnailBadge thumbnailBadgeWarn";
}

function buildSubmissionSummary(photoset: PersistedPhotoset) {
  if (photoset.ingest_job && photoset.ingest_job.status !== "completed") {
    const processedFiles = photoset.ingest_job.processed_files ?? 0;
    const totalFiles = photoset.ingest_job.total_files ?? photoset.entry_count;
    return `Queued for backend ingest • ${processedFiles}/${totalFiles} processed`;
  }

  return [
    `${photoset.accepted_entry_count} accepted`,
    `${photoset.rejected_entry_count} rejected`,
    `${photoset.bucket_counts.lora_only} lora_only`,
    `${photoset.bucket_counts.body_only} body_only`,
    `${photoset.bucket_counts.both} both`
  ].join(" • ");
}

function jobSummaryToDetail(job: IngestJobSummary): IngestJobDetail {
  return {
    bucketCounts: job.bucket_counts,
    errorSummary: null,
    jobPublicId: job.job_public_id,
    processedFiles: job.processed_files,
    progressPercent: job.progress_percent,
    stageHistory: [],
    status: job.status,
    stepName: job.step_name,
    totalFiles: job.total_files
  };
}

function normalizeJobDetail(job: JobDetailResponse): IngestJobDetail {
  return {
    bucketCounts: normalizeBucketCounts(job.progress?.bucket_counts),
    errorSummary: job.error_summary,
    jobPublicId: job.public_id,
    processedFiles: job.progress?.processed_files ?? null,
    progressPercent: job.progress_percent,
    stageHistory: job.stage_history.map((stage) => ({
      bucketCounts: normalizeBucketCounts(stage.bucket_counts),
      createdAt: stage.created_at,
      eventType: stage.event_type,
      processedFiles: stage.processed_files,
      progressPercent: stage.progress_percent,
      status: stage.status,
      stepName: stage.step_name,
      totalFiles: stage.total_files
    })),
    status: job.status,
    stepName: job.step_name,
    totalFiles: job.progress?.total_files ?? null
  };
}

function buildPersistedPreview(entry: PersistedPhotosetEntry): PreviewDialogState {
  return {
    bucket: formatBucketLabel(entry.bucket),
    details: [
      {
        label: "LoRA eligible",
        value: entry.usable_for_lora ? "yes" : "no"
      },
      {
        label: "Body eligible",
        value: entry.usable_for_body ? "yes" : "no"
      },
      {
        label: "Face detected",
        value: entry.qc_metrics.face_detected ? "yes" : "no"
      },
      {
        label: "Body detected",
        value: entry.qc_metrics.body_detected ? "yes" : "no"
      },
      {
        label: "Framing",
        value: entry.qc_metrics.framing_label
      },
      {
        label: "Occlusion",
        value: entry.qc_metrics.occlusion_label
      },
      {
        label: "Blur score",
        value: `${entry.qc_metrics.blur_score}`
      },
      {
        label: "Exposure score",
        value: `${entry.qc_metrics.exposure_score}`
      }
    ],
    imageUrl: entry.artifact_urls.normalized,
    reasonMessages:
      entry.reason_messages.length > 0 ? entry.reason_messages : ["No issues detected."],
    title: entry.original_filename
  };
}

function buildStagedPreview(photo: StagedPhoto): PreviewDialogState {
  return {
    bucket: "pending backend classification",
    details: [
      {
        label: "File size",
        value: formatFileSize(photo.file.size)
      },
      {
        label: "File type",
        value: photo.file.type || "unknown"
      }
    ],
    imageUrl: photo.objectUrl,
    reasonMessages: ["Server-side bucket and QC reasons appear after the upload completes."],
    title: photo.file.name
  };
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
  const [ingestJob, setIngestJob] = React.useState<IngestJobDetail | null>(null);
  const [isLoadingPersisted, setIsLoadingPersisted] = React.useState(false);
  const [isPollingIngest, setIsPollingIngest] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isCreatingCharacter, setIsCreatingCharacter] = React.useState(false);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [previewDialog, setPreviewDialog] = React.useState<PreviewDialogState | null>(null);
  const [submissionSummary, setSubmissionSummary] = React.useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = React.useState<UploadProgressState>({
    bytesUploaded: 0,
    phase: "idle",
    percent: 0,
    totalBytes: 0
  });
  const photosRef = React.useRef<StagedPhoto[]>([]);
  const trimmedCharacterLabel = characterLabel.trim();
  const acceptedEntryCount = persistedPhotoset?.accepted_entry_count ?? 0;
  const rejectedEntryCount = persistedPhotoset?.rejected_entry_count ?? 0;
  const ingestJobPublicId = persistedPhotoset?.ingest_job?.job_public_id ?? ingestJob?.jobPublicId ?? null;
  const ingestStatus = ingestJob?.status ?? persistedPhotoset?.ingest_job?.status ?? null;
  const activeBucketCounts =
    ingestJob?.bucketCounts ??
    persistedPhotoset?.ingest_job?.bucket_counts ??
    persistedPhotoset?.bucket_counts ??
    EMPTY_BUCKET_COUNTS;
  const processedFiles =
    ingestJob?.processedFiles ??
    persistedPhotoset?.ingest_job?.processed_files ??
    (persistedPhotoset?.status === "prepared" ? persistedPhotoset.entry_count : null);
  const totalFiles =
    ingestJob?.totalFiles ??
    persistedPhotoset?.ingest_job?.total_files ??
    persistedPhotoset?.entry_count ??
    photos.length;
  const currentStageName =
    ingestJob?.stepName ??
    persistedPhotoset?.ingest_job?.step_name ??
    (uploadProgress.phase === "server" ? "waiting_for_backend_response" : null);
  const uploadDisabled = trimmedCharacterLabel.length === 0 || photos.length === 0 || isSubmitting;
  const createDisabled =
    !persistedPhotoset ||
    acceptedEntryCount === 0 ||
    isLoadingPersisted ||
    isPollingIngest ||
    isCreatingCharacter ||
    (persistedPhotoset.status !== "prepared" && !isTerminalJobStatus(ingestStatus)) ||
    (ingestStatus !== null && ingestStatus !== "completed");

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
    if (!previewDialog) {
      return undefined;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setPreviewDialog(null);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [previewDialog]);

  const refreshPersistedPhotoset = React.useCallback(async (photosetId: string) => {
    const response = await fetch(`${getApiBase()}/api/v1/photosets/${photosetId}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error("Unable to load the saved QC results.");
    }

    const payload = (await response.json()) as PersistedPhotoset;
    setPersistedPhotoset(payload);
    setSubmissionSummary(buildSubmissionSummary(payload));
    if (payload.character_label) {
      setCharacterLabel(payload.character_label);
    }
    return payload;
  }, []);

  React.useEffect(() => {
    if (!currentPhotosetId) {
      setPersistedPhotoset(null);
      setIngestJob(null);
      return;
    }

    const controller = new AbortController();

    async function loadPhotoset() {
      setIsLoadingPersisted(true);
      setLoadError(null);

      try {
        const response = await fetch(`${getApiBase()}/api/v1/photosets/${currentPhotosetId}`, {
          cache: "no-store",
          signal: controller.signal
        });

        if (!response.ok) {
          throw new Error("Unable to load the uploaded photoset.");
        }

        const payload = (await response.json()) as PersistedPhotoset;
        if (controller.signal.aborted) {
          return;
        }

        setPersistedPhotoset(payload);
        setIngestJob(payload.ingest_job ? jobSummaryToDetail(payload.ingest_job) : null);
        setSubmissionSummary(buildSubmissionSummary(payload));
        if (payload.character_label) {
          setCharacterLabel(payload.character_label);
        }
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

  React.useEffect(() => {
    if (!ingestJobPublicId) {
      return;
    }

    let cancelled = false;
    let timer: number | undefined;

    async function pollIngestJob() {
      setIsPollingIngest(true);

      try {
        const response = await fetch(`${getApiBase()}/api/v1/jobs/${ingestJobPublicId}`, {
          cache: "no-store"
        });

        if (!response.ok) {
          throw new Error("Unable to refresh the ingest job state.");
        }

        const payload = (await response.json()) as JobDetailResponse;

        if (cancelled) {
          return;
        }

        const nextJob = normalizeJobDetail(payload);
        setIngestJob(nextJob);
        setLoadError(null);

        if (nextJob.status === "completed") {
          setUploadProgress((current) =>
            current.phase === "idle"
              ? current
              : {
                  ...current,
                  phase: "complete",
                  percent: 100
                }
          );
          if (currentPhotosetId) {
            await refreshPersistedPhotoset(currentPhotosetId);
          }
          setIsPollingIngest(false);
          return;
        }

        if (nextJob.status === "failed" || nextJob.status === "canceled") {
          setUploadProgress((current) => ({
            ...current,
            phase: "failed"
          }));
          setIsPollingIngest(false);
          return;
        }

        timer = window.setTimeout(pollIngestJob, 1200);
      } catch (error) {
        if (cancelled) {
          return;
        }

        setLoadError(
          error instanceof Error ? error.message : "Unable to refresh the ingest job state."
        );
        timer = window.setTimeout(pollIngestJob, 1200);
      }
    }

    void pollIngestJob();

    return () => {
      cancelled = true;
      if (timer !== undefined) {
        window.clearTimeout(timer);
      }
    };
  }, [currentPhotosetId, ingestJobPublicId, refreshPersistedPhotoset]);

  const onDrop = React.useCallback(
    (acceptedFiles: File[]) => {
      if (currentPhotosetId) {
        window.history.replaceState({}, "", "/studio/characters/new");
        setCurrentPhotosetId(null);
        setPersistedPhotoset(null);
        setIngestJob(null);
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
      setPreviewDialog(null);
      setSubmissionSummary(null);
      setIsCreatingCharacter(false);
      setUploadProgress({
        bytesUploaded: 0,
        phase: "idle",
        percent: 0,
        totalBytes: 0
      });
    },
    [currentPhotosetId]
  );

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
    setPreviewDialog(null);
  }

  function clearPhotos() {
    photos.forEach((photo) => URL.revokeObjectURL(photo.objectUrl));
    setPhotos([]);
    setLoadError(null);
    setPreviewDialog(null);
    setSubmissionSummary(null);
    setIsCreatingCharacter(false);
    setUploadProgress({
      bytesUploaded: 0,
      phase: "idle",
      percent: 0,
      totalBytes: 0
    });
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData();
    const totalBytes = photos.reduce((sum, photo) => sum + photo.file.size, 0);

    formData.set("character_label", trimmedCharacterLabel);
    photos.forEach((photo) => {
      formData.append("photos", photo.file, photo.file.name);
    });

    try {
      setIsSubmitting(true);
      setLoadError(null);
      setPreviewDialog(null);
      setSubmissionSummary(null);
      setIsCreatingCharacter(false);
      setUploadProgress({
        bytesUploaded: 0,
        phase: "uploading",
        percent: 0,
        totalBytes
      });

      const uploadedPhotoset = await new Promise<PersistedPhotoset>((resolve, reject) => {
        const request = new XMLHttpRequest();
        request.open("POST", `${getApiBase()}/api/v1/photosets`);

        request.upload.onprogress = (progressEvent) => {
          if (!progressEvent.lengthComputable) {
            return;
          }

          setUploadProgress({
            bytesUploaded: progressEvent.loaded,
            phase: "uploading",
            percent:
              progressEvent.total > 0
                ? Math.round((progressEvent.loaded / progressEvent.total) * 100)
                : 0,
            totalBytes: progressEvent.total
          });
        };

        request.upload.onload = () => {
          setUploadProgress((current) => ({
            ...current,
            bytesUploaded: current.totalBytes,
            phase: "server",
            percent: 100
          }));
        };

        request.onerror = () => {
          reject(new Error("Photoset upload failed."));
        };

        request.onload = () => {
          let responsePayload: PersistedPhotoset | { detail?: string } | null = null;

          try {
            responsePayload = JSON.parse(request.responseText) as PersistedPhotoset;
          } catch {
            responsePayload = null;
          }

          if (request.status < 200 || request.status >= 300) {
            const detail =
              responsePayload &&
              "detail" in responsePayload &&
              typeof responsePayload.detail === "string"
                ? responsePayload.detail
                : "Photoset upload failed.";
            reject(new Error(detail));
            return;
          }

          resolve(responsePayload as PersistedPhotoset);
        };

        request.send(formData);
      });

      photos.forEach((photo) => URL.revokeObjectURL(photo.objectUrl));
      setPhotos([]);
      setPersistedPhotoset(uploadedPhotoset);
      setCurrentPhotosetId(uploadedPhotoset.public_id);
      setIngestJob(uploadedPhotoset.ingest_job ? jobSummaryToDetail(uploadedPhotoset.ingest_job) : null);
      setSubmissionSummary(buildSubmissionSummary(uploadedPhotoset));
      setUploadProgress((current) => ({
        ...current,
        phase:
          uploadedPhotoset.ingest_job && uploadedPhotoset.ingest_job.status === "completed"
            ? "complete"
            : "server",
        percent: 100
      }));
      window.history.replaceState(
        {},
        "",
        `/studio/characters/new?photoset=${uploadedPhotoset.public_id}`
      );
    } catch (error) {
      setLoadError(
        error instanceof Error
          ? error.message
          : "Upload failed before the backend ingest state became available."
      );
      setUploadProgress((current) => ({
        ...current,
        phase: "failed"
      }));
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
      const response = await fetch(`${getApiBase()}/api/v1/characters`, {
        body: JSON.stringify({ photoset_public_id: persistedPhotoset.public_id }),
        headers: {
          "content-type": "application/json"
        },
        method: "POST"
      });
      const payload = (await response.json().catch(() => null)) as
        | { detail?: string; public_id?: string }
        | null;

      if (!response.ok) {
        throw new Error(payload?.detail ?? "Character creation failed.");
      }

      const createdCharacter = payload as CreatedCharacter;
      const previewResponse = await fetch(
        `${getApiBase()}/api/v1/exports/characters/${createdCharacter.public_id}/preview`,
        { method: "POST" }
      );
      const previewPayload = (await previewResponse.json().catch(() => null)) as
        | { detail?: string }
        | QueuedJobResponse
        | null;

      if (!previewResponse.ok) {
        throw new Error(previewPayload?.detail ?? "Preview export queue request failed.");
      }

      router.push(`/studio/characters/${createdCharacter.public_id}`);
    } catch (error) {
      setLoadError(
        error instanceof Error
          ? error.message
          : "Base character creation failed before the detail route could load."
      );
      setIsCreatingCharacter(false);
    }
  }

  return (
    <div className="characterImportMain">
      <SectionCard
        title="Truthful intake setup"
        description="Enter a required label, upload the photoset with browser transfer progress, then review backend-reported ingest buckets before creating a saved character."
      >
        <div className="statusStrip" role="status" aria-live="polite">
          <span className="statusBadge">1. label the intake</span>
          <span className="statusBadge">2. upload with transfer progress</span>
          <span className="statusBadge">3. inspect server buckets</span>
          <span className="statusBadge">4. create only after ingest completes</span>
        </div>

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
              placeholder="Required character label"
              aria-describedby="character-label-help"
              required
            />
            <p id="character-label-help" className="secondaryNote">
              Labels may repeat. The saved IDs stay unique.
            </p>
          </div>

          <div className="fieldStack">
            <FieldHeader field={PHOTOSET_FIELD} />
            <div
              {...getRootProps({
                "aria-label": "Photoset dropzone",
                className: isDragActive
                  ? "dropzoneSurface dropzoneSurfaceActive"
                  : "dropzoneSurface",
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
                Select PNG, JPEG, or WEBP files. The browser shows transfer progress first, then
                the saved ingest record shows the backend stage and buckets.
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

          <div className="ingestProgressPanel" role="status" aria-live="polite">
            <div className="ingestProgressGrid">
              <article className="ingestProgressCard">
                <strong>Selected files</strong>
                <span>{photos.length > 0 ? `${photos.length} staged locally` : "No files selected yet"}</span>
              </article>
              <article className="ingestProgressCard">
                <strong>Transfer progress</strong>
                <span>
                  {uploadProgress.phase === "idle"
                    ? "Transfer has not started."
                    : `${formatFileSize(uploadProgress.bytesUploaded)} / ${formatFileSize(uploadProgress.totalBytes)} (${uploadProgress.percent}%)`}
                </span>
              </article>
              <article className="ingestProgressCard">
                <strong>Server stage</strong>
                <span>{formatStageLabel(currentStageName)}</span>
              </article>
              <article className="ingestProgressCard">
                <strong>Server file progress</strong>
                <span>
                  {totalFiles && processedFiles !== null
                    ? `${processedFiles} / ${totalFiles} processed`
                    : "Waiting for server counts"}
                </span>
              </article>
            </div>
            <div
              className="jobProgressBar"
              aria-label="Photoset transfer progress"
              aria-valuemax={100}
              aria-valuemin={0}
              aria-valuenow={uploadProgress.percent}
              role="progressbar"
            >
              <div className="jobProgressBarFill" style={{ width: `${uploadProgress.percent}%` }} />
            </div>
            <div className="bucketSummaryGrid" data-testid="bucket-summary">
              {(["lora_only", "body_only", "both", "rejected"] as BucketName[]).map((bucket) => (
                <article key={bucket} className="bucketSummaryCard">
                  <span className={bucketBadgeClassName(bucket)}>{formatBucketLabel(bucket)}</span>
                  <strong>{bucketCountValue(activeBucketCounts, bucket)}</strong>
                </article>
              ))}
            </div>
            {ingestJob?.stageHistory.length ? (
              <ul className="ingestStageList">
                {ingestJob.stageHistory
                  .filter((stage) => stage.stepName)
                  .map((stage, index) => (
                    <li key={`${stage.createdAt}-${index}`}>
                      {`${formatStageLabel(stage.stepName)} (${stage.processedFiles ?? 0}/${stage.totalFiles ?? totalFiles ?? 0})`}
                    </li>
                  ))}
              </ul>
            ) : null}
            {uploadProgress.phase === "server" ? (
              <p className="secondaryNote">
                Transfer finished. Waiting for the backend ingest state to settle.
              </p>
            ) : null}
          </div>

          <div className="characterImportActionRow">
            <span className="secondaryNote">
              {trimmedCharacterLabel.length === 0
                ? "Enter a label before upload can start."
                : photos.length === 0
                  ? "Select at least one photo to start intake."
                  : `Ready to upload ${photos.length} file(s) for ${trimmedCharacterLabel}.`}
            </span>
            <button type="submit" className="themeToggle" disabled={uploadDisabled}>
              {isSubmitting
                ? uploadProgress.phase === "server"
                  ? "Waiting for backend ingest"
                  : `Uploading ${uploadProgress.percent}%`
                : "Upload photoset"}
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

          {persistedPhotoset ? (
            <div className="statusStrip" role="status" aria-live="polite">
              <span className="statusBadge">{`${acceptedEntryCount} accepted`}</span>
              <span className="statusBadge">{`${rejectedEntryCount} rejected`}</span>
              <span className="statusBadge">pass and warn can build</span>
            </div>
          ) : null}
        </form>
      </SectionCard>

      <SectionCard
        title="Thumbnail inspection"
        description="Every thumbnail opens a larger preview. Persisted previews show only backend-reported buckets, reasons, and QC signals."
      >
        {photos.length > 0 ? (
          <div className="thumbnailGrid" data-testid="thumbnail-grid">
            {photos.map((photo) => (
              <article key={photo.id} className="thumbnailCard" data-testid="thumbnail-card">
                <button
                  type="button"
                  className="thumbnailButton"
                  onClick={() => setPreviewDialog(buildStagedPreview(photo))}
                  aria-label={`Inspect ${photo.file.name}`}
                >
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
                    <span className="thumbnailBadge">Pending backend classification</span>
                  </div>
                </button>
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
                <button
                  type="button"
                  className="thumbnailButton"
                  onClick={() => setPreviewDialog(buildPersistedPreview(entry))}
                  aria-label={`Inspect ${entry.original_filename}`}
                >
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
                    <span>
                      {entry.accepted_for_character_use
                        ? "Accepted for character use"
                        : "Rejected from character use"}
                    </span>
                    <span className={bucketBadgeClassName(entry.bucket)}>
                      {formatBucketLabel(entry.bucket)}
                    </span>
                    <span className={badgeClassName(entry.qc_status)}>{`QC ${entry.qc_status}`}</span>
                  </div>
                </button>
                <ul className="thumbnailReasonList">
                  {(entry.reason_messages.length > 0 ? entry.reason_messages : ["No issues detected."]).map(
                    (reason) => (
                      <li key={reason}>{reason}</li>
                    )
                  )}
                </ul>
              </article>
            ))}
          </div>
        ) : isLoadingPersisted ? (
          <EmptyState
            title="Loading saved QC results"
            description="The intake route is reloading the persisted photoset and its backend ingest state."
          />
        ) : (
          <EmptyState
            title="No photos staged yet"
            description="Select a labeled photoset to inspect transfer progress, backend buckets, and the saved thumbnail review state."
          />
        )}

        {persistedPhotoset ? (
          <div className="characterImportActionRow">
            <span className="secondaryNote">
              {createDisabled
                ? "Create saved character stays disabled until ingest completes and at least one accepted image exists."
                : `${acceptedEntryCount} accepted image(s) are available for character creation. ${rejectedEntryCount} rejected image(s) remain visible for review.`}
            </span>
            <button
              type="button"
              className="themeToggle"
              onClick={handleCreateCharacter}
              disabled={createDisabled}
            >
              {isCreatingCharacter ? "Building character" : "Build base character"}
            </button>
          </div>
        ) : null}
      </SectionCard>

      {previewDialog ? (
        <div
          className="thumbnailDialogBackdrop"
          role="presentation"
          onClick={() => setPreviewDialog(null)}
        >
          <div
            className="thumbnailDialogCard"
            role="dialog"
            aria-modal="true"
            aria-labelledby="thumbnail-preview-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="jobProgressHeader">
              <div className="thumbnailMeta">
                <strong id="thumbnail-preview-title">{previewDialog.title}</strong>
                <span className="thumbnailBadge">{previewDialog.bucket}</span>
              </div>
              <button
                type="button"
                className="themeToggle"
                onClick={() => setPreviewDialog(null)}
              >
                Close preview
              </button>
            </div>

            <div className="thumbnailDialogBody">
              <img
                className="thumbnailDialogImage"
                src={previewDialog.imageUrl}
                alt={`Large preview of ${previewDialog.title}`}
                width={720}
                height={720}
              />
              <div className="thumbnailDialogDetails">
                <div className="bucketSummaryGrid">
                  {previewDialog.details.map((detail) => (
                    <article key={detail.label} className="bucketSummaryCard">
                      <span>{detail.label}</span>
                      <strong>{detail.value}</strong>
                    </article>
                  ))}
                </div>
                <strong>Reason details</strong>
                <ul className="thumbnailReasonList">
                  {previewDialog.reasonMessages.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
