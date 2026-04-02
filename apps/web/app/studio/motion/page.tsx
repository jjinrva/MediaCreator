import React from "react";

import { MotionAssignmentPanel } from "../../../components/motion-assignment-panel/MotionAssignmentPanel";
import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";
import { getApiBase } from "../../../lib/runtimeApiBase";

type MotionScreenPayload = {
  characters: Array<{
    current_motion: {
      action_payload_path: string;
      compatible_rig_class: string;
      duration_seconds: number;
      motion_asset_public_id: string;
      motion_name: string;
      motion_slug: string;
      source: string;
    } | null;
    label: string;
    public_id: string;
    status: string;
  }>;
  import_note: string;
  motion_library: Array<{
    action_payload_path: string;
    compatible_rig_class: string;
    duration_seconds: number;
    external_import_note: string;
    name: string;
    public_id: string;
    recommended_external_source: string;
    slug: string;
    source: string;
  }>;
};


async function getMotionScreen(): Promise<MotionScreenPayload> {
  const response = await fetch(`${getApiBase()}/api/v1/motion`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load the motion library.");
  }
  return (await response.json()) as MotionScreenPayload;
}

export default async function MotionPage() {
  const payload = await getMotionScreen();

  return (
    <StudioFrame currentPath="/studio/motion" phaseLabel="Phase 23">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">rig-driven clips</span>
        <span className="statusBadge">seeded library</span>
        <span className="statusBadge">preview-linked</span>
      </div>

      <PageHeader
        eyebrow="Phase 23"
        title="Motion library"
        summary="Choose a real character, assign one reusable motion clip, and carry that motion reference into the Blender preview job payload instead of faking motion with AI-only video."
        actions={<span className="headerCallout">{`${payload.motion_library.length} clip(s)`}</span>}
      />

      <SectionCard
        title="Motion assignment"
        description="Phase 23 seeds the first local Rigify-compatible action library: idle, walk, jump, sit, and turn. External humanoid imports stay optional."
      >
        <MotionAssignmentPanel
          characters={payload.characters.map((character) => ({
            currentMotion: character.current_motion
              ? {
                  actionPayloadPath: character.current_motion.action_payload_path,
                  compatibleRigClass: character.current_motion.compatible_rig_class,
                  durationSeconds: character.current_motion.duration_seconds,
                  motionAssetPublicId: character.current_motion.motion_asset_public_id,
                  motionName: character.current_motion.motion_name,
                  motionSlug: character.current_motion.motion_slug,
                  source: character.current_motion.source
                }
              : null,
            label: character.label,
            publicId: character.public_id,
            status: character.status
          }))}
          importNote={payload.import_note}
          motionLibrary={payload.motion_library.map((motion) => ({
            actionPayloadPath: motion.action_payload_path,
            compatibleRigClass: motion.compatible_rig_class,
            durationSeconds: motion.duration_seconds,
            externalImportNote: motion.external_import_note,
            name: motion.name,
            publicId: motion.public_id,
            recommendedExternalSource: motion.recommended_external_source,
            slug: motion.slug,
            source: motion.source
          }))}
        />
      </SectionCard>
    </StudioFrame>
  );
}
