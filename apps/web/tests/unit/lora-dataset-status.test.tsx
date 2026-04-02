import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LoraDatasetStatus } from "../../components/lora-dataset-status/LoraDatasetStatus";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh
  })
}));

describe("Phase 20 LoRA dataset controls", () => {
  it("requests the LoRA dataset build and refreshes the route", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({
        dataset: {
          detail: "LoRA dataset manifest is available and the prompt expansion contract is ready to audit.",
          status: "available"
        }
      }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <LoraDatasetStatus
        characterPublicId="phase-20-character"
        detail="No LoRA dataset has been built yet. The prompt expansion contract is still visible."
        promptExpansion="character_phase_20, Phase 20 dataset subject, single person, character reference"
        promptHandle="@character_phase-20"
        status="not-ready"
        visibleTags={["character_phase-20", "single-person"]}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Build LoRA dataset" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://10.0.0.102:8010/api/v1/lora-datasets/characters/phase-20-character",
        { method: "POST" }
      );
      expect(refresh).toHaveBeenCalled();
    });
  });
});
