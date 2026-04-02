/* eslint-disable @next/next/no-img-element */

import React from "react";
import { notFound } from "next/navigation";

import { BodyParameterEditor } from "../../../../components/body-editor/BodyParameterEditor";
import { FaceParameterEditor } from "../../../../components/face-editor/FaceParameterEditor";
import { GlbPreview } from "../../../../components/glb-preview/GlbPreview";
import { PageHeader } from "../../../../components/ui/PageHeader";
import { PoseParameterEditor } from "../../../../components/pose-editor/PoseParameterEditor";
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

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://127.0.0.1:8010";

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

export default async function CharacterDetailPage({
  params
}: {
  params: { publicId: string };
}) {
  const [character, exportsPayload, bodyParameters, poseState, facialParameters] = await Promise.all([
    getCharacterDetail(params.publicId),
    getCharacterExports(params.publicId),
    getCharacterBodyParameters(params.publicId),
    getCharacterPoseState(params.publicId),
    getCharacterFacialParameters(params.publicId)
  ]);
  const title = character.label ?? `Character ${character.public_id.slice(0, 8)}`;

  return (
    <StudioFrame currentPath="/studio/characters/new" phaseLabel="Phase 17">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">registry asset</span>
        <span className="statusBadge">history recorded</span>
        <span className="statusBadge">api-backed detail</span>
      </div>

      <PageHeader
        eyebrow="Phase 17"
        title={title}
        summary={`This character detail route now persists body, pose, and face controls from the API, and the Outputs section can now generate a truthful Blender-backed preview GLB.`}
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
          description="The GLB preview path and final export destination are API-backed now, and Phase 17 can generate a real Blender preview GLB through the local Rigify export job."
        >
          <GlbPreview
            alt={`${title} GLB preview`}
            characterPublicId={character.public_id}
            detail={exportsPayload.preview_glb.detail}
            src={exportsPayload.preview_glb.url}
            status={exportsPayload.preview_glb.status}
          />
          <dl className="keyValueList">
            <div className="keyValueRow">
              <dt>Preview GLB</dt>
              <dd>{exportsPayload.preview_glb.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Final GLB export</dt>
              <dd>{exportsPayload.final_glb.status}</dd>
            </div>
            <div className="keyValueRow">
              <dt>Export job</dt>
              <dd>{exportsPayload.export_job.status}</dd>
            </div>
          </dl>
        </SectionCard>
      </div>
    </StudioFrame>
  );
}
