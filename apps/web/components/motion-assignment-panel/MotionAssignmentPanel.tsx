"use client";

import { useRouter } from "next/navigation";
import React from "react";

type MotionAssignmentPanelProps = {
  characters: Array<{
    currentMotion:
      | {
          actionPayloadPath: string;
          compatibleRigClass: string;
          durationSeconds: number;
          motionAssetPublicId: string;
          motionName: string;
          motionSlug: string;
          source: string;
        }
      | null;
    label: string;
    publicId: string;
    status: string;
  }>;
  importNote: string;
  motionLibrary: Array<{
    actionPayloadPath: string;
    compatibleRigClass: string;
    durationSeconds: number;
    externalImportNote: string;
    name: string;
    publicId: string;
    recommendedExternalSource: string;
    slug: string;
    source: string;
  }>;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

export function MotionAssignmentPanel({
  characters,
  importNote,
  motionLibrary
}: MotionAssignmentPanelProps) {
  const router = useRouter();
  const [selectedCharacterId, setSelectedCharacterId] = React.useState(
    characters[0]?.publicId ?? ""
  );
  const [selectedMotionId, setSelectedMotionId] = React.useState(motionLibrary[0]?.publicId ?? "");
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [actionSummary, setActionSummary] = React.useState<string | null>(null);
  const [isSaving, setIsSaving] = React.useState(false);

  const selectedCharacter = characters.find((character) => character.publicId === selectedCharacterId);
  const selectedMotion = motionLibrary.find((motion) => motion.publicId === selectedMotionId);

  async function handleAssignMotion(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCharacterId || !selectedMotionId) {
      setActionError("Choose both a character and a motion clip before assigning.");
      return;
    }

    try {
      setActionError(null);
      setActionSummary(null);
      setIsSaving(true);

      const response = await fetch(
        `${API_BASE_URL}/api/v1/motion/characters/${selectedCharacterId}`,
        {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ motion_public_id: selectedMotionId })
        }
      );
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) {
        throw new Error(payload.detail ?? "Motion assignment failed.");
      }

      setActionSummary("Motion assigned to character.");
      router.refresh();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Motion assignment failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="sectionCardBody">
      <div className="keyValueRow">
        <dt>Import policy</dt>
        <dd>{importNote}</dd>
      </div>

      <div className="thumbnailGrid">
        <form className="thumbnailCard" onSubmit={(event) => void handleAssignMotion(event)}>
          <div className="thumbnailMeta fieldStack">
            <strong>Assign motion</strong>
            <label htmlFor="motion-character-select">Character</label>
            <select
              id="motion-character-select"
              className="textInput"
              value={selectedCharacterId}
              onChange={(event) => setSelectedCharacterId(event.target.value)}
              disabled={characters.length === 0}
            >
              {characters.length === 0 ? <option value="">No characters available</option> : null}
              {characters.map((character) => (
                <option key={character.publicId} value={character.publicId}>
                  {character.label}
                </option>
              ))}
            </select>
            <label htmlFor="motion-clip-select">Motion clip</label>
            <select
              id="motion-clip-select"
              className="textInput"
              value={selectedMotionId}
              onChange={(event) => setSelectedMotionId(event.target.value)}
              disabled={motionLibrary.length === 0}
            >
              {motionLibrary.length === 0 ? <option value="">No motion clips available</option> : null}
              {motionLibrary.map((motion) => (
                <option key={motion.publicId} value={motion.publicId}>
                  {motion.name}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="previewActionButton"
              disabled={isSaving || characters.length === 0 || motionLibrary.length === 0}
            >
              {isSaving ? "Assigning motion..." : "Assign motion"}
            </button>
          </div>
        </form>

        <article className="thumbnailCard">
          <div className="thumbnailMeta fieldStack">
            <strong>Current preview reference</strong>
            <span>{selectedCharacter ? selectedCharacter.label : "No character selected"}</span>
            <span>
              {selectedCharacter?.currentMotion
                ? `Current motion: ${selectedCharacter.currentMotion.motionName}`
                : "Current motion: none"}
            </span>
            {selectedMotion ? (
              <>
                <span>{`Selected clip: ${selectedMotion.name}`}</span>
                <span>{`Rig class: ${selectedMotion.compatibleRigClass}`}</span>
                <span>{`Duration: ${selectedMotion.durationSeconds}s`}</span>
                <pre className="promptAuditBlock">{selectedMotion.actionPayloadPath}</pre>
              </>
            ) : null}
          </div>
        </article>
      </div>

      {actionError ? (
        <span className="previewActionError" role="alert">
          {actionError}
        </span>
      ) : null}
      {actionSummary ? (
        <span className="previewActionSummary" role="status">
          {actionSummary}
        </span>
      ) : null}

      <div className="thumbnailGrid">
        {motionLibrary.map((motion) => (
          <article key={motion.publicId} className="thumbnailCard">
            <div className="thumbnailMeta">
              <strong>{motion.name}</strong>
              <span>{motion.slug}</span>
              <span className="thumbnailBadge">{motion.source}</span>
              <span>{`Rig class: ${motion.compatibleRigClass}`}</span>
              <span>{`Duration: ${motion.durationSeconds}s`}</span>
              <span>{`External source: ${motion.recommendedExternalSource}`}</span>
              <pre className="promptAuditBlock">{motion.actionPayloadPath}</pre>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
