import React from "react";

import { PageHeader } from "../../../../components/ui/PageHeader";
import { StudioFrame } from "../../../../components/ui/StudioFrame";
import { CaptureGuideSidebar } from "../../../../components/character-import/CaptureGuideSidebar";
import { CharacterImportIngest } from "../../../../components/character-import/CharacterImportIngest";

export default function NewCharacterPage() {
  return (
    <StudioFrame currentPath="/studio/characters/new" phaseLabel="Phase 11">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">photoset upload</span>
        <span className="statusBadge">base character create</span>
        <span className="statusBadge">capture guide inline</span>
      </div>

      <PageHeader
        eyebrow="Phase 11"
        title="New character ingest"
        summary="Upload a guided photoset, reload the stored QC output from FastAPI, and create one API-backed base character record that redirects to its public detail route."
        actions={<span className="headerCallout">No demo characters or fake registry rows are shown here.</span>}
      />

      <div className="characterImportLayout">
        <CharacterImportIngest />
        <CaptureGuideSidebar />
      </div>
    </StudioFrame>
  );
}
