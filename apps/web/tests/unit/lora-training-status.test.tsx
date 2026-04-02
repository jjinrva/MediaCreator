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
        trainingJobProgressPercent={null}
        trainingJobPublicId={null}
        trainingJobStatus="not-queued"
        trainingJobStepName={null}
      />
    );

    expect(screen.getByRole("button", { name: "Train LoRA locally" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("posts the training request and refreshes when the trainer is ready", async () => {
    const fetchMock = vi.fn(async (input: string) => {
      if (input.endsWith("/api/v1/lora/characters/phase-21-character")) {
        return {
          json: async () => ({
            training_job: {
              detail: "LoRA training queued. Follow the job until it reaches a terminal state.",
              job_public_id: "job-lora-1",
              progress_percent: 0,
              status: "queued",
              step_name: "queued"
            }
          }),
          ok: true
        };
      }

      throw new Error(`Unexpected fetch: ${input}`);
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
        trainingJobDetail="No LoRA training job has been queued yet."
        trainingJobProgressPercent={null}
        trainingJobPublicId={null}
        trainingJobStatus="not-queued"
        trainingJobStepName={null}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Train LoRA locally" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8010/api/v1/lora/characters/phase-21-character",
        { method: "POST" }
      );
      expect(screen.getByText("LoRA training job:queued:job-lora-1")).toBeTruthy();
      expect(refresh).not.toHaveBeenCalled();
    });
  });
});
