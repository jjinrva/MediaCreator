import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { GlbPreview } from "../../components/glb-preview/GlbPreview";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh
  })
}));

describe("Phase 17 GLB preview controls", () => {
  it("requests a Blender preview export and refreshes the route", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({
        export_job: {
          detail: "Latest Blender preview export job completed successfully.",
          status: "completed"
        },
        preview_glb: {
          detail: "Preview GLB exported from the Blender Rigify runtime is available.",
          status: "available"
        }
      }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <GlbPreview
        alt="Phase 17 preview"
        characterPublicId="phase-17-character"
        detail="No GLB preview is available yet."
        src={null}
        status="not-ready"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Generate preview GLB" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://127.0.0.1:8010/api/v1/exports/characters/phase-17-character/preview",
        { method: "POST" }
      );
      expect(refresh).toHaveBeenCalled();
    });
  });
});
