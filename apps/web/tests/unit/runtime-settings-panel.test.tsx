import React from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { RuntimeSettingsPanel } from "../../app/studio/settings/RuntimeSettingsPanel";

afterEach(() => {
  cleanup();
});

describe("Phase 26 runtime settings panel", () => {
  it("renders truthful capability and storage-path details", () => {
    render(
      <RuntimeSettingsPanel
        aiToolkit={{
          aiToolkitBin: null,
          detail:
            "LoRA training is unavailable because AI Toolkit is missing or NAS-backed storage is not ready.",
          lorasRoot: "/mnt/nas/mediacreator/models/loras",
          missingRequirements: ["ai_toolkit_missing"],
          status: "unavailable"
        }}
        blender={{
          blenderBin: "/opt/blender-4.5-lts/blender",
          detail: "Blender 4.5 LTS is available for preview/video render jobs.",
          status: "ready"
        }}
        generation={{
          checkpointsRoot: "/mnt/nas/mediacreator/models/checkpoints",
          comfyuiBaseUrl: null,
          comfyuiBaseUrlConfigured: false,
          comfyuiServiceReachable: false,
          discoveredWorkflowFiles: [],
          embeddingsRoot: "/mnt/nas/mediacreator/models/embeddings",
          lorasRoot: "/mnt/nas/mediacreator/models/loras",
          missingRequirements: ["comfyui_base_url_missing", "checkpoint_files_missing"],
          modelRootsOnNas: true,
          requiredWorkflowFiles: ["text_to_image_v1.json", "character_refine_img2img_v1.json"],
          status: "unavailable",
          vaesRoot: "/mnt/nas/mediacreator/models/vaes",
          workflowsRoot: "/opt/MediaCreator/workflows/comfyui"
        }}
        nasAvailable={true}
        storageMode="nas"
        storagePaths={{
          characterAssetsRoot: "/mnt/nas/mediacreator/characters",
          checkpointsRoot: "/mnt/nas/mediacreator/models/checkpoints",
          embeddingsRoot: "/mnt/nas/mediacreator/models/embeddings",
          exportsRoot: "/mnt/nas/mediacreator/exports",
          lorasRoot: "/mnt/nas/mediacreator/models/loras",
          modelsRoot: "/mnt/nas/mediacreator/models",
          nasRoot: "/mnt/nas/mediacreator",
          preparedImagesRoot: "/mnt/nas/mediacreator/photos/prepared",
          rendersRoot: "/mnt/nas/mediacreator/renders",
          scratchRoot: "/scratch/mediacreator",
          uploadedPhotosRoot: "/mnt/nas/mediacreator/photos/uploaded",
          vaesRoot: "/mnt/nas/mediacreator/models/vaes",
          wardrobeRoot: "/mnt/nas/mediacreator/wardrobe"
        }}
      />
    );

    expect(screen.getByText("Single-user runtime only. No fake readiness is shown here.")).toBeTruthy();
    expect(screen.getByText("ComfyUI generation")).toBeTruthy();
    expect(screen.getByText("/opt/MediaCreator/workflows/comfyui")).toBeTruthy();
    expect(screen.getByText("/mnt/nas/mediacreator")).toBeTruthy();
    expect(screen.getByText("ai_toolkit_missing")).toBeTruthy();
    expect(screen.getByText("/opt/blender-4.5-lts/blender")).toBeTruthy();
  });
});
