import React from "react";

import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";
import { getApiBase } from "../../../lib/runtimeApiBase";
import { GenerationWorkspace } from "./GenerationWorkspace";

type WorkspacePayload = {
  characters: Array<{
    label: string;
    prompt_expansion: string;
    prompt_handle: string;
    public_id: string;
    status: string;
    training_prompt_status: string;
    visible_tags: string[];
  }>;
  civitai_import: {
    base_url: string;
    detail: string;
    missing_requirements: string[];
    status: string;
  };
  external_loras: Array<{
    character_public_id: string | null;
    model_name: string;
    owner_label: string;
    prompt_handle: string;
    registry_public_id: string;
    source: string;
    status: string;
    storage_path: string | null;
    toolkit_name: string | null;
  }>;
  generation_capability: {
    detail: string;
    missing_requirements: string[];
    status: string;
  };
  local_loras: Array<{
    character_public_id: string | null;
    model_name: string;
    owner_label: string;
    prompt_handle: string;
    registry_public_id: string;
    source: string;
    status: string;
    storage_path: string | null;
    toolkit_name: string | null;
  }>;
  recent_requests: Array<{
    created_at: string;
    expanded_prompt: string;
    external_lora:
      | {
          model_name: string;
          registry_public_id: string;
        }
      | null;
    local_lora:
      | {
          model_name: string;
          registry_public_id: string;
        }
      | null;
    matched_handles: string[];
    provider_status: string;
    public_id: string;
    raw_prompt: string;
    status: string;
    target_kind: string;
    workflow_id: string;
    workflow_path: string;
  }>;
  workflow_contracts: Array<{
    path: string;
    target_kind: string;
    workflow_id: string;
  }>;
};


async function getWorkspace(): Promise<WorkspacePayload> {
  const response = await fetch(`${getApiBase()}/api/v1/generation`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load the generation workspace.");
  }
  return (await response.json()) as WorkspacePayload;
}

export default async function GeneratePage() {
  const workspace = await getWorkspace();

  return (
    <StudioFrame currentPath="/studio/generate" phaseLabel="Phase 25">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">separate workspace</span>
        <span className="statusBadge">@character expansion</span>
        <span className="statusBadge">registry-backed loras</span>
      </div>

      <PageHeader
        eyebrow="Phase 25"
        title="Generation workspace"
        summary="Stage standalone image or video generation prompts away from the 3D editing routes, show the full visible `@character` expansion, and only allow LoRAs through the internal registry."
        actions={<span className="headerCallout">{`${workspace.characters.length} handle(s)`}</span>}
      />

      <SectionCard
        title="Prompt workspace"
        description="Phase 25 keeps the prompt contract auditable. The workspace stores the expanded prompt and linked model references truthfully even when ComfyUI is not yet ready to emit media."
      >
        <GenerationWorkspace
          characters={workspace.characters.map((character) => ({
            label: character.label,
            promptExpansion: character.prompt_expansion,
            promptHandle: character.prompt_handle,
            publicId: character.public_id,
            status: character.status,
            trainingPromptStatus: character.training_prompt_status,
            visibleTags: character.visible_tags
          }))}
          civitaiImport={{
            baseUrl: workspace.civitai_import.base_url,
            detail: workspace.civitai_import.detail,
            missingRequirements: workspace.civitai_import.missing_requirements,
            status: workspace.civitai_import.status
          }}
          externalLoras={workspace.external_loras.map((lora) => ({
            characterPublicId: lora.character_public_id,
            modelName: lora.model_name,
            ownerLabel: lora.owner_label,
            promptHandle: lora.prompt_handle,
            registryPublicId: lora.registry_public_id,
            source: lora.source,
            status: lora.status,
            storagePath: lora.storage_path,
            toolkitName: lora.toolkit_name
          }))}
          generationCapability={{
            detail: workspace.generation_capability.detail,
            missingRequirements: workspace.generation_capability.missing_requirements,
            status: workspace.generation_capability.status
          }}
          localLoras={workspace.local_loras.map((lora) => ({
            characterPublicId: lora.character_public_id,
            modelName: lora.model_name,
            ownerLabel: lora.owner_label,
            promptHandle: lora.prompt_handle,
            registryPublicId: lora.registry_public_id,
            source: lora.source,
            status: lora.status,
            storagePath: lora.storage_path,
            toolkitName: lora.toolkit_name
          }))}
          recentRequests={workspace.recent_requests.map((request) => ({
            createdAt: request.created_at,
            expandedPrompt: request.expanded_prompt,
            externalLora: request.external_lora
              ? {
                  modelName: request.external_lora.model_name,
                  registryPublicId: request.external_lora.registry_public_id
                }
              : null,
            localLora: request.local_lora
              ? {
                  modelName: request.local_lora.model_name,
                  registryPublicId: request.local_lora.registry_public_id
                }
              : null,
            matchedHandles: request.matched_handles,
            providerStatus: request.provider_status,
            publicId: request.public_id,
            rawPrompt: request.raw_prompt,
            status: request.status,
            targetKind: request.target_kind,
            workflowId: request.workflow_id,
            workflowPath: request.workflow_path
          }))}
          workflowContracts={workspace.workflow_contracts.map((workflow) => ({
            path: workflow.path,
            targetKind: workflow.target_kind,
            workflowId: workflow.workflow_id
          }))}
        />
      </SectionCard>
    </StudioFrame>
  );
}
