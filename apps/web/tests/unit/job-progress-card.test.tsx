import React from "react";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { JobProgressCard } from "../../components/jobs/JobProgressCard";

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

describe("Phase 04 job progress card", () => {
  it("refreshes the route when a queued job reaches completion", async () => {
    const fetchMock = vi.fn(async (input: string) => {
      if (input.endsWith("/jobs/job-1")) {
        return {
          json: async () => ({
            error_summary: null,
            finished_at: "2026-04-02T00:00:01Z",
            job_type: "blender-preview-export",
            output_asset_id: "asset-1",
            output_storage_object_id: "storage-1",
            progress_percent: 100,
            public_id: "job-1",
            started_at: "2026-04-02T00:00:00Z",
            status: "completed",
            step_name: "completed"
          }),
          ok: true
        };
      }

      if (input.endsWith("/system/status")) {
        return {
          json: async () => ({
            worker: {
              detail: "The 'worker' heartbeat is current and reports 'polling'.",
              last_seen_at: "2026-04-02T00:00:00Z",
              seconds_since_heartbeat: 0,
              service_name: "worker",
              stale_after_seconds: 15,
              status: "ready"
            }
          }),
          ok: true
        };
      }

      throw new Error(`Unexpected fetch: ${input}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <JobProgressCard
        initialJob={{
          detail: "Preview export queued. Follow the job until it reaches a terminal state.",
          jobPublicId: "job-1",
          progressPercent: 0,
          status: "queued",
          stepName: "queued"
        }}
        title="Preview generation job"
      />
    );

    await waitFor(() => {
      expect(refresh).toHaveBeenCalled();
      expect(screen.getByText("completed")).toBeTruthy();
    });
  });

  it("shows the worker stale state clearly while the job stays queued", async () => {
    const fetchMock = vi.fn(async (input: string) => {
      if (input.endsWith("/jobs/job-2")) {
        return {
          json: async () => ({
            error_summary: null,
            finished_at: null,
            job_type: "character-motion-video-render",
            output_asset_id: null,
            output_storage_object_id: null,
            progress_percent: 0,
            public_id: "job-2",
            started_at: null,
            status: "queued",
            step_name: "queued"
          }),
          ok: true
        };
      }

      if (input.endsWith("/system/status")) {
        return {
          json: async () => ({
            worker: {
              detail:
                "The 'worker' heartbeat is stale. Last seen 20s ago while reporting 'polling'.",
              last_seen_at: "2026-04-02T00:00:00Z",
              seconds_since_heartbeat: 20,
              service_name: "worker",
              stale_after_seconds: 15,
              status: "stale"
            }
          }),
          ok: true
        };
      }

      throw new Error(`Unexpected fetch: ${input}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <JobProgressCard
        initialJob={{
          detail: "Controlled video render queued. Follow the job until it reaches a terminal state.",
          jobPublicId: "job-2",
          progressPercent: 0,
          status: "queued",
          stepName: "queued"
        }}
        title="Controlled video render job"
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Worker stale:/)).toBeTruthy();
    });

    expect(refresh).not.toHaveBeenCalled();
  });
});
