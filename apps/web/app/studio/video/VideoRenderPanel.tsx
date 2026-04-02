"use client";

import Link from "next/link";
import React from "react";

import { JobProgressCard } from "../../../components/jobs/JobProgressCard";
import type { JobProgressSummary } from "../../../lib/jobProgress";
import { isInFlightJobStatus } from "../../../lib/jobProgress";
import { getApiBase } from "../../../lib/runtimeApiBase";

type VideoRenderPanelProps = {
  characters: Array<{
    currentMotion:
      | {
          actionPayloadPath: string;
          compatibleRigClass: string;
          durationSeconds: number;
          motionAssetPublicId: string;
          motionName: string;
          motionSlug: string;
          source: string;
        }
      | null;
    label: string;
    latestVideo:
      | {
          createdAt: string;
          durationSeconds: number;
          fileSizeBytes: number | null;
          height: number;
          jobPublicId: string | null;
          motionAssetPublicId: string;
          motionName: string;
          publicId: string;
          status: string;
          storageObjectPublicId: string | null;
          url: string | null;
          width: number;
        }
      | null;
    publicId: string;
    renderHistory: Array<{
      createdAt: string;
      details: Record<string, unknown>;
      eventType: string;
      publicId: string;
    }>;
    renderJob: {
      detail: string;
      jobPublicId: string | null;
      progressPercent: number | null;
      publicId: string | null;
      status: string;
      stepName: string | null;
    };
    status: string;
  }>;
  renderPolicy: string;
};


function formatBytes(byteCount: number | null) {
  if (byteCount === null) {
    return "unknown";
  }
  if (byteCount < 1024) {
    return `${byteCount} B`;
  }
  return `${(byteCount / 1024 / 1024).toFixed(2)} MB`;
}

export function VideoRenderPanel({ characters, renderPolicy }: VideoRenderPanelProps) {
  const [selectedCharacterId, setSelectedCharacterId] = React.useState(characters[0]?.publicId ?? "");
  const [width, setWidth] = React.useState(480);
  const [height, setHeight] = React.useState(480);
  const [durationSeconds, setDurationSeconds] = React.useState("1.1");
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isRendering, setIsRendering] = React.useState(false);
  const [queuedJobs, setQueuedJobs] = React.useState<Record<string, JobProgressSummary>>({});

  const selectedCharacter = characters.find((character) => character.publicId === selectedCharacterId);
  const selectedCharacterJob =
    selectedCharacter === undefined
      ? null
      : queuedJobs[selectedCharacter.publicId] ?? {
          detail: selectedCharacter.renderJob.detail,
          jobPublicId: selectedCharacter.renderJob.jobPublicId,
          progressPercent: selectedCharacter.renderJob.progressPercent,
          status: selectedCharacter.renderJob.status,
          stepName: selectedCharacter.renderJob.stepName
        };
  const hasTrackedJob =
    selectedCharacterJob !== null &&
    selectedCharacterJob.jobPublicId !== null &&
    selectedCharacterJob.status !== "not-queued";
  const isJobInFlight =
    selectedCharacterJob !== null && isInFlightJobStatus(selectedCharacterJob.status);

  React.useEffect(() => {
    if (!selectedCharacter) {
      return;
    }

    setWidth(selectedCharacter.latestVideo?.width ?? 480);
    setHeight(selectedCharacter.latestVideo?.height ?? 480);
    setDurationSeconds(
      String(selectedCharacter.latestVideo?.durationSeconds ?? selectedCharacter.currentMotion?.durationSeconds ?? 1.1)
    );
  }, [selectedCharacter]);

  async function handleRenderVideo(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCharacter) {
      setActionError("Choose a character before rendering.");
      return;
    }
    if (!selectedCharacter.currentMotion) {
      setActionError("Assign a motion clip before rendering a controlled video.");
      return;
    }

    try {
      setIsRendering(true);
      setActionError(null);
      setActionSummary(null);

      const response = await fetch(
        `${getApiBase()}/api/v1/video/characters/${selectedCharacter.publicId}/render`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            duration_seconds: Number(durationSeconds),
            height,
            width
          })
        }
      );
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Video render failed.");
      }

      const queuedRenderJob = payload as {
        detail: string;
        job_public_id: string;
        progress_percent: number;
        status: string;
        step_name: string | null;
      };
      setQueuedJobs((currentJobs) => ({
        ...currentJobs,
        [selectedCharacter.publicId]: {
          detail: queuedRenderJob.detail,
          jobPublicId: queuedRenderJob.job_public_id,
          progressPercent: queuedRenderJob.progress_percent,
          status: queuedRenderJob.status,
          stepName: queuedRenderJob.step_name
        }
      }));
      setActionSummary(queuedRenderJob.detail);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Video render failed.");
    } finally {
      setIsRendering(false);
    }
  }

  return (
    <div className="sectionCardBody">
      <div className="keyValueRow">
        <dt>Render policy</dt>
        <dd>{renderPolicy}</dd>
      </div>

      <div className="thumbnailGrid">
        <form className="thumbnailCard" onSubmit={(event) => void handleRenderVideo(event)}>
          <div className="thumbnailMeta fieldStack">
            <strong>Render clip</strong>
            <label htmlFor="video-character-select">Character</label>
            <select
              id="video-character-select"
              className="textInput"
              value={selectedCharacterId}
              onChange={(event) => setSelectedCharacterId(event.target.value)}
              disabled={characters.length === 0}
            >
              {characters.length === 0 ? <option value="">No characters available</option> : null}
              {characters.map((character) => (
                <option key={character.publicId} value={character.publicId}>
                  {character.label}
                </option>
              ))}
            </select>
            <label htmlFor="video-render-width">Width</label>
            <input
              id="video-render-width"
              className="textInput"
              type="number"
              min={256}
              max={1080}
              step={32}
              value={width}
              onChange={(event) => setWidth(Number(event.target.value))}
            />
            <label htmlFor="video-render-height">Height</label>
            <input
              id="video-render-height"
              className="textInput"
              type="number"
              min={256}
              max={1080}
              step={32}
              value={height}
              onChange={(event) => setHeight(Number(event.target.value))}
            />
            <label htmlFor="video-render-duration">Duration (seconds)</label>
            <input
              id="video-render-duration"
              className="textInput"
              type="number"
              min={0.5}
              max={5}
              step={0.1}
              value={durationSeconds}
              onChange={(event) => setDurationSeconds(event.target.value)}
            />
            <button
              type="submit"
              className="previewActionButton"
              disabled={
                isRendering ||
                isJobInFlight ||
                !selectedCharacter ||
                !selectedCharacter.currentMotion
              }
            >
              {isRendering
                ? "Queueing video render..."
                : isJobInFlight
                  ? "Video render in progress..."
                  : "Render video"}
            </button>
          </div>
        </form>

        <article className="thumbnailCard">
          <div className="thumbnailMeta fieldStack">
            <strong>Selected character</strong>
            <span>{selectedCharacter?.label ?? "No character selected"}</span>
            <span>{selectedCharacter?.currentMotion ? `Current motion: ${selectedCharacter.currentMotion.motionName}` : "Current motion: none"}</span>
            <span>{`Render job: ${selectedCharacterJob?.status ?? "not-queued"}`}</span>
            <span>{selectedCharacterJob?.detail ?? "No render job has been queued yet."}</span>
            {selectedCharacter?.latestVideo ? (
              <>
                <span>{`Latest video: ${selectedCharacter.latestVideo.motionName}`}</span>
                <span>{`Resolution: ${selectedCharacter.latestVideo.width}x${selectedCharacter.latestVideo.height}`}</span>
                <span>{`Duration: ${selectedCharacter.latestVideo.durationSeconds}s`}</span>
                <span>{`File size: ${formatBytes(selectedCharacter.latestVideo.fileSizeBytes)}`}</span>
                {selectedCharacter.latestVideo.url ? (
                  <>
                    <video
                      key={selectedCharacter.latestVideo.publicId}
                      data-testid="rendered-video"
                      controls
                      muted
                      playsInline
                      preload="metadata"
                      src={selectedCharacter.latestVideo.url}
                      style={{ width: "100%", borderRadius: "1rem" }}
                    />
                    <Link className="previewActionButton" href={selectedCharacter.latestVideo.url}>
                      Download MP4
                    </Link>
                  </>
                ) : (
                  <span>Latest video asset exists but no playable file is available yet.</span>
                )}
              </>
            ) : (
              <span>No rendered video is available yet.</span>
            )}
            {selectedCharacterJob && hasTrackedJob ? (
              <JobProgressCard initialJob={selectedCharacterJob} title="Controlled video render job" />
            ) : null}
          </div>
        </article>
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

      <div className="sectionCardBody">
        <strong>Render history</strong>
        {selectedCharacter?.renderHistory.length ? (
          <ol className="historyList">
            {selectedCharacter.renderHistory.map((event) => (
              <li key={event.publicId} className="historyItem">
                <strong>{event.eventType}</strong>
                <span>{new Date(event.createdAt).toLocaleString()}</span>
                <span>{JSON.stringify(event.details)}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p>No controlled video history exists for this character yet.</p>
        )}
      </div>
    </div>
  );
}
