import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ReconstructionStatus } from "../../components/reconstruction-status/ReconstructionStatus";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh
  })
}));

describe("Phase 18 reconstruction controls", () => {
  it("requests the high-detail path and refreshes the route", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({
        reconstruction: {
          reconstruction_job: {
            detail: "Latest high-detail reconstruction job completed successfully.",
            status: "completed"
          }
        }
      }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <ReconstructionStatus
        characterPublicId="phase-18-character"
        detail="The riggable base GLB is available, but the current capture set has not produced a detail-prep artifact."
        detailLevel="riggable-base-only"
        jobStatus="not-queued"
        strategy="smplx-stage1-only"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Run high-detail path" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://10.0.0.102:8010/api/v1/exports/characters/phase-18-character/reconstruction",
        { method: "POST" }
      );
      expect(refresh).toHaveBeenCalled();
    });
  });
});
