import Link from "next/link";
import React from "react";
import { APP_NAME } from "@mediacreator/shared-types";

const unfinishedFeatures = [
  "MediaCreator is running in single-user mode for this rebuild.",
  "PostgreSQL runs locally through Docker Compose for the local runtime.",
  "Canonical long-lived assets require a mounted NAS root.",
  "If the NAS mount is missing, MediaCreator drops to degraded local-only storage mode.",
  "Generation stays unavailable until ComfyUI, NAS model roots, and versioned workflow JSONs are detected.",
  "The new /studio shell exposes accessible tabs, shared UI primitives, and permanent info icons for visible inputs.",
  "Not all screens are finished yet, and unfinished areas stay labeled truthfully.",
  "The worker now claims PostgreSQL-backed jobs and records truthful queue state as work progresses."
];

export default function HomePage() {
  return (
    <main className="homeShell">
      <section className="homeHero panel" aria-labelledby="home-title">
        <span className="eyebrow">Single-user rebuild</span>
        <h1 id="home-title">{APP_NAME}</h1>
        <p>
          The local runtime foundation is live. Phase 07 adds the permanent studio shell while
          keeping the landing route honest about what is ready and what is still staged.
        </p>
        <div className="homeActions">
          <Link href="/studio" className="primaryLink">
            Open studio shell
          </Link>
          <span className="secondaryNote">No fake assets or sample jobs are shown.</span>
        </div>
        <ul>
          {unfinishedFeatures.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
