import Link from "next/link";
import React from "react";

import { KeyValueList } from "../ui/KeyValueList";
import { SectionCard } from "../ui/SectionCard";
import { CAPTURE_REQUIREMENTS, CAPTURE_STEPS, RISK_NOTES } from "../../app/studio/capture-guide/content";

export function CaptureGuideSidebar() {
  return (
    <div className="characterImportSidebar">
      <SectionCard
        title="Capture guide"
        description="Keep the Phase 08 guidance visible while you stage the photoset."
      >
        <KeyValueList items={[...CAPTURE_REQUIREMENTS].slice(0, 3)} />
      </SectionCard>

      <SectionCard
        title="Quick reminders"
        description="These are the minimum reminders that should stay beside the ingest grid."
      >
        <ul className="captureGuideList">
          {CAPTURE_STEPS.slice(0, 3).map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </SectionCard>

      <SectionCard
        title="Before upload starts"
        description="Phase 09 is truthful about what the browser knows and what the backend has not done yet."
      >
        <ul className="captureGuideList">
          {RISK_NOTES.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
        <Link href="/studio/capture-guide" className="inlineLink">
          Open the full capture guide
        </Link>
      </SectionCard>
    </div>
  );
}
