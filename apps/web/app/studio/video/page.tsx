import React from "react";

import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";
import { getApiBase } from "../../../lib/runtimeApiBase";
import { VideoRenderPanel } from "./VideoRenderPanel";

type VideoScreenPayload = {
  characters: Array<{
    current_motion: {
      action_payload_path: string;
      compatible_rig_class: string;
      duration_seconds: number;
      motion_asset_public_id: string;
      motion_name: string;
      motion_slug: string;
      source: string;
    } | null;
    label: string;
    latest_video: {
      created_at: string;
      duration_seconds: number;
      file_size_bytes: number | null;
      height: number;
      job_public_id: string | null;
      motion_asset_public_id: string;
      motion_name: string;
      public_id: string;
      status: string;
      storage_object_public_id: string | null;
      url: string | null;
      width: number;
    } | null;
    public_id: string;
    render_history: Array<{
      created_at: string;
      details: Record<string, unknown>;
      event_type: string;
      public_id: string;
    }>;
    render_job: {
      detail: string;
      job_public_id: string | null;
      progress_percent: number | null;
      public_id: string | null;
      status: string;
      step_name: string | null;
    };
    status: string;
  }>;
  render_policy: string;
};


async function getVideoScreen(): Promise<VideoScreenPayload> {
  const response = await fetch(`${getApiBase()}/api/v1/video`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load the controlled video route.");
  }
  return (await response.json()) as VideoScreenPayload;
}

export default async function VideoPage() {
  const payload = await getVideoScreen();

  return (
    <StudioFrame currentPath="/studio/video" phaseLabel="Phase 24">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">blender background render</span>
        <span className="statusBadge">rig-driven motion</span>
        <span className="statusBadge">mp4 output</span>
      </div>

      <PageHeader
        eyebrow="Phase 24"
        title="Controlled video rendering"
        summary="Render a real rig-driven Blender motion clip from the assigned character action, store the MP4 as a tracked asset, and surface a truthful player instead of substituting AI video generation."
        actions={<span className="headerCallout">{`${payload.characters.length} character(s)`}</span>}
      />

      <SectionCard
        title="Video output"
        description="The first video path keeps the camera and scene simple on purpose. The requirement here is controlled motion on a rigged character and a persisted MP4 with lineage."
      >
        <VideoRenderPanel
          characters={payload.characters.map((character) => ({
            currentMotion: character.current_motion
              ? {
                  actionPayloadPath: character.current_motion.action_payload_path,
                  compatibleRigClass: character.current_motion.compatible_rig_class,
                  durationSeconds: character.current_motion.duration_seconds,
                  motionAssetPublicId: character.current_motion.motion_asset_public_id,
                  motionName: character.current_motion.motion_name,
                  motionSlug: character.current_motion.motion_slug,
                  source: character.current_motion.source
                }
              : null,
            label: character.label,
            latestVideo: character.latest_video
              ? {
                  createdAt: character.latest_video.created_at,
                  durationSeconds: character.latest_video.duration_seconds,
                  fileSizeBytes: character.latest_video.file_size_bytes,
                  height: character.latest_video.height,
                  jobPublicId: character.latest_video.job_public_id,
                  motionAssetPublicId: character.latest_video.motion_asset_public_id,
                  motionName: character.latest_video.motion_name,
                  publicId: character.latest_video.public_id,
                  status: character.latest_video.status,
                  storageObjectPublicId: character.latest_video.storage_object_public_id,
                  url: character.latest_video.url,
                  width: character.latest_video.width
                }
              : null,
            publicId: character.public_id,
            renderHistory: character.render_history.map((event) => ({
              createdAt: event.created_at,
              details: event.details,
              eventType: event.event_type,
              publicId: event.public_id
            })),
            renderJob: {
              detail: character.render_job.detail,
              jobPublicId: character.render_job.job_public_id,
              progressPercent: character.render_job.progress_percent,
              publicId: character.render_job.public_id,
              status: character.render_job.status,
              stepName: character.render_job.step_name
            },
            status: character.status
          }))}
          renderPolicy={payload.render_policy}
        />
      </SectionCard>
    </StudioFrame>
  );
}
