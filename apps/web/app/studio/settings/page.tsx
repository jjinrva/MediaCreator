import React from "react";

import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";
import { getApiBase } from "../../../lib/runtimeApiBase";
import { RuntimeSettingsPanel } from "./RuntimeSettingsPanel";

type SystemStatusPayload = {
  ai_toolkit: {
    ai_toolkit_bin: string | null;
    detail: string;
    loras_root: string;
    missing_requirements: string[];
    status: string;
  };
  application: string;
  blender: {
    blender_bin: string;
    detail: string;
    status: string;
  };
  generation: {
    checkpoints_root: string;
    comfyui_base_url: string | null;
    comfyui_base_url_configured: boolean;
    comfyui_service_reachable: boolean;
    discovered_workflow_files: string[];
    embeddings_root: string;
    loras_root: string;
    missing_requirements: string[];
    model_roots_on_nas: boolean;
    required_workflow_files: string[];
    status: string;
    vaes_root: string;
    workflows_root: string;
  };
  mode: string;
  nas_available: boolean;
  service: string;
  storage_mode: string;
  storage_paths: {
    character_assets_root: string;
    checkpoints_root: string;
    embeddings_root: string;
    exports_root: string;
    loras_root: string;
    models_root: string;
    nas_root: string;
    prepared_images_root: string;
    renders_root: string;
    scratch_root: string;
    uploaded_photos_root: string;
    vaes_root: string;
    wardrobe_root: string;
  };
};


async function getSystemStatus(): Promise<SystemStatusPayload> {
  const response = await fetch(`${getApiBase()}/api/v1/system/status`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load the runtime settings.");
  }
  return (await response.json()) as SystemStatusPayload;
}

export default async function SettingsPage() {
  const payload = await getSystemStatus();

  return (
    <StudioFrame currentPath="/studio/settings" phaseLabel="Phase 26">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">{payload.mode}</span>
        <span className="statusBadge">{payload.generation.status} generation</span>
        <span className="statusBadge">{payload.blender.status} blender</span>
        <span className="statusBadge">{payload.ai_toolkit.status} ai toolkit</span>
      </div>

      <PageHeader
        eyebrow="Phase 26"
        title="Runtime settings"
        summary="Expose only the real runtime configuration for this single-user build: active storage roots, ComfyUI capability, Blender capability, and AI Toolkit readiness."
        actions={<span className="headerCallout">{`${payload.application} ${payload.service}`}</span>}
      />

      <SectionCard
        title="Truthful runtime controls"
        description="This page is intentionally read-only. It shows the active runtime roots and capability state without adding unfinished multi-user or permissions settings."
      >
        <RuntimeSettingsPanel
          aiToolkit={{
            aiToolkitBin: payload.ai_toolkit.ai_toolkit_bin,
            detail: payload.ai_toolkit.detail,
            lorasRoot: payload.ai_toolkit.loras_root,
            missingRequirements: payload.ai_toolkit.missing_requirements,
            status: payload.ai_toolkit.status
          }}
          blender={{
            blenderBin: payload.blender.blender_bin,
            detail: payload.blender.detail,
            status: payload.blender.status
          }}
          generation={{
            checkpointsRoot: payload.generation.checkpoints_root,
            comfyuiBaseUrl: payload.generation.comfyui_base_url,
            comfyuiBaseUrlConfigured: payload.generation.comfyui_base_url_configured,
            comfyuiServiceReachable: payload.generation.comfyui_service_reachable,
            discoveredWorkflowFiles: payload.generation.discovered_workflow_files,
            embeddingsRoot: payload.generation.embeddings_root,
            lorasRoot: payload.generation.loras_root,
            missingRequirements: payload.generation.missing_requirements,
            modelRootsOnNas: payload.generation.model_roots_on_nas,
            requiredWorkflowFiles: payload.generation.required_workflow_files,
            status: payload.generation.status,
            vaesRoot: payload.generation.vaes_root,
            workflowsRoot: payload.generation.workflows_root
          }}
          nasAvailable={payload.nas_available}
          storageMode={payload.storage_mode}
          storagePaths={{
            characterAssetsRoot: payload.storage_paths.character_assets_root,
            checkpointsRoot: payload.storage_paths.checkpoints_root,
            embeddingsRoot: payload.storage_paths.embeddings_root,
            exportsRoot: payload.storage_paths.exports_root,
            lorasRoot: payload.storage_paths.loras_root,
            modelsRoot: payload.storage_paths.models_root,
            nasRoot: payload.storage_paths.nas_root,
            preparedImagesRoot: payload.storage_paths.prepared_images_root,
            rendersRoot: payload.storage_paths.renders_root,
            scratchRoot: payload.storage_paths.scratch_root,
            uploadedPhotosRoot: payload.storage_paths.uploaded_photos_root,
            vaesRoot: payload.storage_paths.vaes_root,
            wardrobeRoot: payload.storage_paths.wardrobe_root
          }}
        />
      </SectionCard>
    </StudioFrame>
  );
}
