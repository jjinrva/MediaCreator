import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoraTrainingStatus } from "../../components/lora-training-status/LoraTrainingStatus";

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

describe("Phase 21 LoRA training controls", () => {
  it("keeps the button disabled when AI Toolkit is unavailable", () => {
    render(
      <LoraTrainingStatus
        activeModel={null}
        capabilityDetail="LoRA training is unavailable because AI Toolkit is missing or NAS-backed storage is not ready."
        capabilityStatus="unavailable"
        characterPublicId="phase-21-character"
        datasetStatus="available"
        missingRequirements={["ai_toolkit_missing"]}
        registry={[]}
        trainingJobDetail="No LoRA training job has been queued yet."
        trainingJobStatus="not-queued"
      />
    );

    expect(screen.getByRole("button", { name: "Train LoRA locally" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("posts the training request and refreshes when the trainer is ready", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({
        training_job: {
          detail: "Latest LoRA training job completed successfully.",
          status: "completed"
        }
      }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <LoraTrainingStatus
        activeModel={null}
        capabilityDetail="AI Toolkit is installed and LoRA training can run locally."
        capabilityStatus="ready"
        characterPublicId="phase-21-character"
        datasetStatus="available"
        missingRequirements={[]}
        registry={[{ modelName: "working-run", promptHandle: "@character_ready", status: "working" }]}
        trainingJobDetail="Latest LoRA training job is queued."
        trainingJobStatus="queued"
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Train LoRA locally" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://10.0.0.102:8010/api/v1/lora/characters/phase-21-character",
        { method: "POST" }
      );
      expect(refresh).toHaveBeenCalled();
    });
  });
});
