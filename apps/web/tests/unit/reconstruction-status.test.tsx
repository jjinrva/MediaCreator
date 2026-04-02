import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ReconstructionStatus } from "../../components/reconstruction-status/ReconstructionStatus";

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

describe("Phase 18 reconstruction controls", () => {
  it("queues the high-detail path and renders live job state", async () => {
    const fetchMock = vi.fn(async (input: string) => {
      if (input.endsWith("/reconstruction")) {
        return {
          json: async () => ({
            detail: "High-detail reconstruction queued. Follow the job until it reaches a terminal state.",
            job_public_id: "job-recon-1",
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
      <ReconstructionStatus
        characterPublicId="phase-18-character"
        detail="The riggable base GLB is available, but the current capture set has not produced a detail-prep artifact."
        detailLevel="riggable-base-only"
        jobDetail="The high-detail path has not run yet."
        jobProgressPercent={null}
        jobPublicId={null}
        jobStatus="not-queued"
        jobStepName={null}
        strategy="smplx-stage1-only"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Run high-detail path" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8010/api/v1/exports/characters/phase-18-character/reconstruction",
        { method: "POST" }
      );
      expect(
        screen.getByText("High-detail reconstruction job:queued:job-recon-1")
      ).toBeTruthy();
      expect(refresh).not.toHaveBeenCalled();
    });
  });
});
