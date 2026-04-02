/* eslint-disable @next/next/no-img-element */

import React from "react";
import { notFound } from "next/navigation";

import { BodyParameterEditor } from "../../../../components/body-editor/BodyParameterEditor";
import { FaceParameterEditor } from "../../../../components/face-editor/FaceParameterEditor";
import { GlbPreview } from "../../../../components/glb-preview/GlbPreview";
import { LoraDatasetStatus } from "../../../../components/lora-dataset-status/LoraDatasetStatus";
import { LoraTrainingStatus } from "../../../../components/lora-training-status/LoraTrainingStatus";
import { PageHeader } from "../../../../components/ui/PageHeader";
import { PoseParameterEditor } from "../../../../components/pose-editor/PoseParameterEditor";
import { ReconstructionStatus } from "../../../../components/reconstruction-status/ReconstructionStatus";
import { SectionCard } from "../../../../components/ui/SectionCard";
import { StudioFrame } from "../../../../components/ui/StudioFrame";

type CharacterDetail = {
  accepted_entries: Array<{
    artifact_urls: {
      normalized: string;
      original: string;
      thumbnail: string;
    };
    framing_label: string;
    original_filename: string;
    public_id: string;
    qc_status: "fail" | "pass" | "warn";
  }>;
  accepted_entry_count: number;
  created_at: string;
  history: Array<{
    created_at: string;
    details: Record<string, unknown>;
    event_type: string;
    public_id: string;
  }>;
  label: string | null;
  originating_photoset_public_id: string;
  public_id: string;
  status: string;
};

type CharacterExports = {
  export_job: {
    detail: string;
    status: string;
  };
  final_glb: {
    detail: string;
    status: string;
    url: string | null;
  };
  preview_glb: {
    detail: string;
    status: string;
    url: string | null;
  };
  reconstruction: {
    detail: string;
    detail_level: string;
    detail_prep_artifact: {
      detail: string;
      status: string;
      url: string | null;
    };
    reconstruction_job: {
      detail: string;
      status: string;
    };
    riggable_base_glb: {
      detail: string;
      status: string;
      url: string | null;
    };
    strategy: string;
  };
  texture_material: {
    base_texture_artifact: {
      detail: string;
      status: string;
      url: string | null;
    };
    current_texture_fidelity: string;
    detail: string;
    refined_texture_artifact: {
      detail: string;
      status: string;
      url: string | null;
    };
  };
};

type CharacterBodyParameters = {
  catalog: Array<{
    default_value: number;
    display_label: string;
    group: string;
    help_text: string;
    key: string;
    max_value: number;
    min_value: number;
    step: number;
    unit: string;
  }>;
  current_values: Record<string, number>;
};

type CharacterPoseState = {
  catalog: Array<{
    axis: string;
    bone_name: string;
    default_value: number;
    display_label: string;
    group: string;
    help_text: string;
    key: string;
    max_value: number;
    min_value: number;
    step: number;
    unit: string;
  }>;
  current_values: Record<string, number>;
};

type CharacterFacialParameters = {
  catalog: Array<{
    default_value: number;
    display_label: string;
    group: string;
    help_text: string;
    key: string;
    max_value: number;
    min_value: number;
    shape_key_name: string;
    step: number;
    unit: string;
  }>;
  current_values: Record<string, number>;
};

type CharacterLoraDataset = {
  dataset: {
    dataset_version: string;
    detail: string;
    entry_count: number;
    manifest_url: string | null;
    prompt_contract_version: string;
    prompt_expansion: string;
    prompt_handle: string;
    status: string;
    visible_tags: string[];
  };
};

type CharacterLoraTraining = {
  active_model: {
    model_name: string;
    prompt_handle: string;
    status: string;
    storage_object_public_id: string;
    storage_path: string;
  } | null;
  capability: {
    ai_toolkit_bin: string | null;
    detail: string;
    loras_root: string;
    missing_requirements: string[];
    status: string;
  };
  character_public_id: string;
  registry: Array<{
    details: Record<string, unknown>;
    model_name: string;
    prompt_handle: string;
    public_id: string;
    status: string;
    storage_object_public_id: string | null;
  }>;
  training_job: {
    detail: string;
    status: string;
  };
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

function badgeClassName(status: "fail" | "pass" | "warn") {
  if (status === "pass") {
    return "thumbnailBadge thumbnailBadgePass";
  }
  if (status === "warn") {
    return "thumbnailBadge thumbnailBadgeWarn";
  }
  return "thumbnailBadge thumbnailBadgeFail";
}

async function getCharacterDetail(publicId: string): Promise<CharacterDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character detail route.");
  }

  return (await response.json()) as CharacterDetail;
}

async function getCharacterExports(publicId: string): Promise<CharacterExports> {
  const response = await fetch(`${API_BASE_URL}/api/v1/exports/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character export scaffold.");
  }

  return (await response.json()) as CharacterExports;
}

async function getCharacterBodyParameters(publicId: string): Promise<CharacterBodyParameters> {
  const response = await fetch(`${API_BASE_URL}/api/v1/body/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character body parameters.");
  }

  return (await response.json()) as CharacterBodyParameters;
}

async function getCharacterPoseState(publicId: string): Promise<CharacterPoseState> {
  const response = await fetch(`${API_BASE_URL}/api/v1/pose/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character pose state.");
  }

  return (await response.json()) as CharacterPoseState;
}

async function getCharacterFacialParameters(publicId: string): Promise<CharacterFacialParameters> {
  const response = await fetch(`${API_BASE_URL}/api/v1/face/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character facial parameters.");
  }

  return (await response.json()) as CharacterFacialParameters;
}

async function getCharacterLoraDataset(publicId: string): Promise<CharacterLoraDataset> {
  const response = await fetch(`${API_BASE_URL}/api/v1/lora-datasets/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character LoRA dataset contract.");
  }

  return (await response.json()) as CharacterLoraDataset;
}

async function getCharacterLoraTraining(publicId: string): Promise<CharacterLoraTraining> {
  const response = await fetch(`${API_BASE_URL}/api/v1/lora/characters/${publicId}`, {
    cache: "no-store"
  });

  if (response.status === 404) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Unable to load the character LoRA training status.");
  }

  return (await response.json()) as CharacterLoraTraining;
}

export default async function CharacterDetailPage({
  params
}: {
  params: { publicId: string };
}) {
  const [
    character,
    exportsPayload,
    bodyParameters,
    poseState,
    facialParameters,
    loraDataset,
    loraTraining
  ] = await Promise.all([
    getCharacterDetail(params.publicId),
    getCharacterExports(params.publicId),
    getCharacterBodyParameters(params.publicId),
    getCharacterPoseState(params.publicId),
    getCharacterFacialParameters(params.publicId),
    getCharacterLoraDataset(params.publicId),
    getCharacterLoraTraining(params.publicId)
  ]);
  const title = character.label ?? `Character ${character.public_id.slice(0, 8)}`;

  return (
    <StudioFrame currentPath="/studio/characters/new" phaseLabel="Phase 21">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">registry asset</span>
        <span className="statusBadge">history recorded</span>
        <span className="statusBadge">api-backed detail</span>
      </div>

      <PageHeader
        eyebrow="Phase 21"
        title={title}
        summary={`This detail route now keeps body, pose, face, reconstruction, dataset, and LoRA registry state in sync from the API. Phase 21 adds truthful local LoRA training readiness and active-model reporting without pretending AI Toolkit is installed.`}
        actions={<span className="headerCallout">{character.status}</span>}
      />

      <div className="characterImportMain">
        <SectionCard
          title="Overview"
          description="The base registry record, source photoset, and accepted prepared references are shown here without inventing later-phase values."
        >
          <dl className="keyValueList">
            <div className="keyValueRow">
              <dt>Character public ID</dt>
              <dd>{character.public_id}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Originating photoset</dt>
              <dd>{character.originating_photoset_public_id}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Accepted references</dt>
              <dd>{character.accepted_entry_count}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Created at</dt>
              <dd>{character.created_at}</dd>
            </div>
          </dl>
          <div className="thumbnailGrid">
            {character.accepted_entries.map((entry) => (
              <article key={entry.public_id} className="thumbnailCard">
                <img
                  className="thumbnailPreview"
                  src={entry.artifact_urls.thumbnail}
                  alt={`Accepted reference ${entry.original_filename}`}
                  width={240}
                  height={240}
                />
                <div className="thumbnailMeta">
                  <strong>{entry.original_filename}</strong>
                  <span>{entry.framing_label}</span>
                  <span className={badgeClassName(entry.qc_status)}>{`QC ${entry.qc_status}`}</span>
                </div>
              </article>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="Body"
          description="Move a slider, commit it, persist the canonical value through FastAPI, and let the route refresh from server state. The ranges and tooltips come from the backend catalog."
        >
          <BodyParameterEditor
            characterPublicId={character.public_id}
            initialCatalog={bodyParameters.catalog}
            initialValues={bodyParameters.current_values}
          />
        </SectionCard>

        <SectionCard
          title="Pose"
          description="Move a limb slider, commit it, persist the saved pose state through FastAPI, and let the route refresh from server state so the preview and history stay aligned."
        >
          <PoseParameterEditor
            characterPublicId={character.public_id}
            initialCatalog={poseState.catalog}
            initialValues={poseState.current_values}
          />
        </SectionCard>

        <SectionCard
          title="Face"
          description="Move a facial slider, commit it, persist the saved expression factor through FastAPI, and let the route refresh from server state so future Blender face mapping stays truthful."
        >
          <FaceParameterEditor
            characterPublicId={character.public_id}
            initialCatalog={facialParameters.catalog}
            initialValues={facialParameters.current_values}
          />
        </SectionCard>

        <SectionCard
          title="History"
          description="Only real registry events are shown here. Later phases will extend this same history trail."
        >
          <ol className="historyList">
            {character.history.map((event) => (
              <li key={event.public_id} className="historyItem">
                <strong>{event.event_type}</strong>
                <span>{event.created_at}</span>
              </li>
            ))}
          </ol>
        </SectionCard>

        <SectionCard
          title="Outputs"
          description="The GLB preview path, high-detail reconstruction path, and final export destination are API-backed now. Phase 18 reports the current reconstruction level truthfully and only writes a detail-prep artifact when the capture set qualifies."
        >
          <GlbPreview
            alt={`${title} GLB preview`}
            characterPublicId={character.public_id}
            detail={exportsPayload.preview_glb.detail}
            src={exportsPayload.preview_glb.url}
            status={exportsPayload.preview_glb.status}
            textureFidelity={exportsPayload.texture_material.current_texture_fidelity}
          />
          <ReconstructionStatus
            characterPublicId={character.public_id}
            detail={exportsPayload.reconstruction.detail}
            detailLevel={exportsPayload.reconstruction.detail_level}
            jobStatus={exportsPayload.reconstruction.reconstruction_job.status}
            strategy={exportsPayload.reconstruction.strategy}
          />
          <dl className="keyValueList">
            <div className="keyValueRow">
              <dt>Preview GLB</dt>
              <dd>{exportsPayload.preview_glb.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Preview texture fidelity</dt>
              <dd>{exportsPayload.texture_material.current_texture_fidelity}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Final GLB export</dt>
              <dd>{exportsPayload.final_glb.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Export job</dt>
              <dd>{exportsPayload.export_job.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>High-detail detail level</dt>
              <dd>{exportsPayload.reconstruction.detail_level}</dd>
            </div>
            <div className="keyValueRow">
              <dt>High-detail strategy</dt>
              <dd>{exportsPayload.reconstruction.strategy}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Riggable base asset</dt>
              <dd>{exportsPayload.reconstruction.riggable_base_glb.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Detail-prep artifact</dt>
              <dd>{exportsPayload.reconstruction.detail_prep_artifact.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Reconstruction job</dt>
              <dd>{exportsPayload.reconstruction.reconstruction_job.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Base texture artifact</dt>
              <dd>{exportsPayload.texture_material.base_texture_artifact.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Refined texture artifact</dt>
              <dd>{exportsPayload.texture_material.refined_texture_artifact.status}</dd>
            </div>
          </dl>
        </SectionCard>

        <SectionCard
          title="LoRA Dataset"
          description="Phase 20 keeps the training-set contract auditable: accepted images only, visible prompt expansion, and one versioned dataset folder per character."
        >
          <LoraDatasetStatus
            characterPublicId={character.public_id}
            detail={loraDataset.dataset.detail}
            promptExpansion={loraDataset.dataset.prompt_expansion}
            promptHandle={loraDataset.dataset.prompt_handle}
            status={loraDataset.dataset.status}
            visibleTags={loraDataset.dataset.visible_tags}
          />
          <dl className="keyValueList">
            <div className="keyValueRow">
              <dt>Dataset status</dt>
              <dd>{loraDataset.dataset.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Dataset version</dt>
              <dd>{loraDataset.dataset.dataset_version}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Dataset images</dt>
              <dd>{loraDataset.dataset.entry_count}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Prompt handle</dt>
              <dd>{loraDataset.dataset.prompt_handle}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Prompt contract version</dt>
              <dd>{loraDataset.dataset.prompt_contract_version}</dd>
            </div>
          </dl>
        </SectionCard>

        <SectionCard
          title="LoRA Training"
          description="Phase 21 adds the NAS-backed model registry and the truthful local-training gate. If AI Toolkit is missing, the UI says so and keeps the training action disabled."
        >
          <LoraTrainingStatus
            activeModel={
              loraTraining.active_model
                ? {
                    modelName: loraTraining.active_model.model_name,
                    promptHandle: loraTraining.active_model.prompt_handle,
                    storagePath: loraTraining.active_model.storage_path
                  }
                : null
            }
            capabilityDetail={loraTraining.capability.detail}
            capabilityStatus={loraTraining.capability.status}
            characterPublicId={character.public_id}
            datasetStatus={loraDataset.dataset.status}
            missingRequirements={loraTraining.capability.missing_requirements}
            registry={loraTraining.registry.map((entry) => ({
              modelName: entry.model_name,
              promptHandle: entry.prompt_handle,
              status: entry.status
            }))}
            trainingJobDetail={loraTraining.training_job.detail}
            trainingJobStatus={loraTraining.training_job.status}
          />
          <dl className="keyValueList">
            <div className="keyValueRow">
              <dt>Training capability</dt>
              <dd>{loraTraining.capability.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Latest LoRA job</dt>
              <dd>{loraTraining.training_job.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Registry entries</dt>
              <dd>{loraTraining.registry.length}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Active LoRA</dt>
              <dd>{loraTraining.active_model?.model_name ?? "none"}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Activation prompt handle</dt>
              <dd>{loraTraining.active_model?.prompt_handle ?? "none"}</dd>
            </div>
          </dl>
        </SectionCard>
      </div>
    </StudioFrame>
  );
}
