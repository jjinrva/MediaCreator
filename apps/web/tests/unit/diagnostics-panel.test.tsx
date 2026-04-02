import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DiagnosticsPanel } from "../../app/studio/diagnostics/DiagnosticsPanel";

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
});

describe("Phase 26 diagnostics panel", () => {
  it("renders live checks and refreshes diagnostics on demand", async () => {
    render(
      <DiagnosticsPanel
        checks={[
          {
            checkId: "ingest_pipeline",
            detail: "Latest character has 2 accepted reference image(s).",
            label: "Ingest pipeline",
            status: "pass"
          },
          {
            checkId: "glb_preview",
            detail: "Preview GLB status is 'not-ready'.",
            label: "GLB preview",
            status: "fail"
          }
        ]}
        reportSummary={{
          generatedAt: "2026-04-02T08:00:00Z",
          humanReportPath: "/opt/MediaCreator/docs/verification/final_verify_matrix.md",
          machineReportPath: "/opt/MediaCreator/docs/verification/final_verify_matrix.json",
          overallStatus: "pass"
        }}
      />
    );

    expect(screen.getByText("Failing checks are current truth, not placeholders. Re-run to refresh against live data.")).toBeTruthy();
    expect(screen.getByText("Ingest pipeline")).toBeTruthy();
    expect(screen.getByText("GLB preview")).toBeTruthy();
    expect(screen.getByText("/opt/MediaCreator/docs/verification/final_verify_matrix.md")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Run diagnostics again" }));

    await waitFor(() => {
      expect(refresh).toHaveBeenCalled();
    });
  });
});
