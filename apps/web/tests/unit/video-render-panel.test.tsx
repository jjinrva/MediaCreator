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

beforeEach(() => {
  refresh.mockReset();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Phase 24 video render panel", () => {
  it("posts a controlled video render request and keeps the current video playable", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({ characters: [{}] }),
      ok: true
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
              url: "http://10.0.0.102:8010/api/v1/video/assets/video-1.mp4",
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
              publicId: "job-1",
              status: "completed"
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
        "http://10.0.0.102:8010/api/v1/video/characters/character-1/render",
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
      expect(refresh).toHaveBeenCalled();
    });
  });
});
