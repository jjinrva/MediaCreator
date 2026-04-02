import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { VideoRenderPanel } from "../../app/studio/video/VideoRenderPanel";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh
  })
}));

vi.mock("../../components/jobs/JobProgressCard", () => ({
  JobProgressCard: ({
    initialJob,
    title
  }: {
    initialJob: { jobPublicId: string | null; status: string };
    title: string;
  }) => <div>{`${title}:${initialJob.status}:${initialJob.jobPublicId}`}</div>
}));

beforeEach(() => {
  refresh.mockReset();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Phase 24 video render panel", () => {
  it("queues a controlled video render request and keeps the current video playable", async () => {
    const fetchMock = vi.fn(async (input: string) => {
      if (input.endsWith("/render")) {
        return {
          json: async () => ({
            detail: "Controlled video render queued. Follow the job until it reaches a terminal state.",
            job_public_id: "job-video-1",
            progress_percent: 0,
            status: "queued",
            step_name: "queued"
          }),
          ok: true
        };
      }

      throw new Error(`Unexpected fetch: ${input}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <VideoRenderPanel
        characters={[
          {
            currentMotion: {
              actionPayloadPath: "/opt/MediaCreator/motions/library/jump.json",
              compatibleRigClass: "rigify-human-v1",
              durationSeconds: 1.1,
              motionAssetPublicId: "motion-jump",
              motionName: "Jump",
              motionSlug: "jump",
              source: "local-seeded"
            },
            label: "Video character",
            latestVideo: {
              createdAt: "2026-04-02T00:00:00Z",
              durationSeconds: 1.1,
              fileSizeBytes: 2048,
              height: 320,
              jobPublicId: "job-1",
              motionAssetPublicId: "motion-jump",
              motionName: "Jump",
              publicId: "video-1",
              status: "available",
              storageObjectPublicId: "storage-1",
              url: "http://localhost:8010/api/v1/video/assets/video-1.mp4",
              width: 320
            },
            publicId: "character-1",
            renderHistory: [
              {
                createdAt: "2026-04-02T00:00:00Z",
                details: { motion_name: "Jump" },
                eventType: "video.output_registered",
                publicId: "history-1"
              }
            ],
            renderJob: {
              detail: "Latest controlled video render job completed successfully.",
              jobPublicId: "job-1",
              progressPercent: 100,
              publicId: "job-1",
              status: "completed",
              stepName: "completed"
            },
            status: "available"
          }
        ]}
        renderPolicy="Rig-driven Blender rendering only."
      />
    );

    expect(screen.getByTestId("rendered-video")).toBeTruthy();

    fireEvent.change(screen.getByLabelText("Width"), {
      target: { value: "352" }
    });
    fireEvent.change(screen.getByLabelText("Height"), {
      target: { value: "288" }
    });
    fireEvent.change(screen.getByLabelText("Duration (seconds)"), {
      target: { value: "1.4" }
    });
    fireEvent.submit(screen.getByRole("button", { name: "Render video" }).closest("form")!);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8010/api/v1/video/characters/character-1/render",
        {
          body: JSON.stringify({
            duration_seconds: 1.4,
            height: 288,
            width: 352
          }),
          headers: { "content-type": "application/json" },
          method: "POST"
        }
      );
      expect(screen.getByText("Controlled video render job:queued:job-video-1")).toBeTruthy();
      expect(refresh).not.toHaveBeenCalled();
    });
  });
});
