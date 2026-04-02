import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GlbPreview } from "../../components/glb-preview/GlbPreview";

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

describe("Phase 17 GLB preview controls", () => {
  it("queues a Blender preview export and renders live job state", async () => {
    const fetchMock = vi.fn(async (input: string) => {
      if (input.endsWith("/preview")) {
        return {
          json: async () => ({
            detail: "Preview export queued. Follow the job until it reaches a terminal state.",
            job_public_id: "job-preview-1",
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
      <GlbPreview
        alt="Phase 17 preview"
        characterPublicId="phase-17-character"
        detail="No GLB preview is available yet."
        jobDetail="No Blender export job has been queued yet."
        jobProgressPercent={null}
        jobPublicId={null}
        jobStatus="not-queued"
        jobStepName={null}
        src={null}
        status="not-ready"
        textureFidelity="untextured"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Generate preview GLB" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8010/api/v1/exports/characters/phase-17-character/preview",
        { method: "POST" }
      );
      expect(screen.getByText("Texture fidelity: untextured")).toBeTruthy();
      expect(screen.getByText("Preview generation job:queued:job-preview-1")).toBeTruthy();
      expect(refresh).not.toHaveBeenCalled();
    });
  });
});
