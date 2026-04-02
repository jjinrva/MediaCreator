import React from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GenerationWorkspace } from "../../app/studio/generate/GenerationWorkspace";

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

describe("Phase 25 generation workspace", () => {
  it("shows visible handle expansion and stores generation requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      json: async () => ({ public_id: "request-1" }),
      ok: true
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <GenerationWorkspace
        characters={[
          {
            label: "Hang",
            promptExpansion: "character_hang, Hang, single person, character reference",
            promptHandle: "@character_hang",
            publicId: "character-1",
            status: "available",
            trainingPromptStatus: "not-ready",
            visibleTags: ["character_hang"]
          }
        ]}
        civitaiImport={{
          baseUrl: "https://civitai.com/api/v1",
          detail: "Civitai discovery/import is disabled until the opt-in flag and NAS-backed storage are both ready.",
          missingRequirements: ["civitai_import_disabled"],
          status: "disabled"
        }}
        externalLoras={[]}
        generationCapability={{
          detail:
            "Generation requests are stored truthfully, but media output is not claimed until ComfyUI capability is ready.",
          missingRequirements: ["comfyui_base_url_missing"],
          status: "unavailable"
        }}
        localLoras={[
          {
            characterPublicId: "character-1",
            modelName: "hang-current.safetensors",
            ownerLabel: "Hang",
            promptHandle: "@phase25_local",
            registryPublicId: "registry-1",
            source: "local",
            status: "current",
            storagePath: "/mnt/nas/mediacreator/models/loras/trained/current.safetensors",
            toolkitName: "ai-toolkit"
          }
        ]}
        recentRequests={[]}
        workflowContracts={[
          {
            path: "/opt/MediaCreator/workflows/comfyui/text_to_image_v1.json",
            targetKind: "image",
            workflowId: "text_to_image_v1"
          },
          {
            path: "/opt/MediaCreator/workflows/comfyui/text_to_video_v1.json",
            targetKind: "video",
            workflowId: "text_to_video_v1"
          }
        ]}
      />
    );

    fireEvent.change(screen.getByLabelText("Prompt"), {
      target: { value: "@character_hang standing on a bridge" }
    });

    expect(screen.getByTestId("expanded-prompt-preview").textContent).toContain("Hang");
    expect(screen.getByTestId("expanded-prompt-preview").textContent).toContain(
      "standing on a bridge"
    );

    fireEvent.change(screen.getByLabelText("Local LoRA"), {
      target: { value: "registry-1" }
    });
    fireEvent.submit(
      screen.getByRole("button", { name: "Store generation request" }).closest("form")!
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith("http://10.0.0.102:8010/api/v1/generation/requests", {
        body: JSON.stringify({
          external_lora_registry_public_id: null,
          local_lora_registry_public_id: "registry-1",
          prompt_text: "@character_hang standing on a bridge",
          target_kind: "image"
        }),
        headers: { "content-type": "application/json" },
        method: "POST"
      });
      expect(refresh).toHaveBeenCalled();
    });
  });
});
