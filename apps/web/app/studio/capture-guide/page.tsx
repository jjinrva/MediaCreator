import { access } from "fs/promises";
import path from "path";

import Image from "next/image";
import React from "react";

import { FileTile } from "../../../components/ui/FileTile";
import { KeyValueList } from "../../../components/ui/KeyValueList";
import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";
import {
  ASSET_DIRECTORY_RELATIVE_PATH,
  BACKGROUNDS_TO_AVOID,
  BLENDER_SCRIPT_RELATIVE_PATH,
  CAPTURE_ASSET_GROUPS,
  CAPTURE_REQUIREMENTS,
  CAPTURE_STEPS,
  DOCS_GUIDE_RELATIVE_PATH,
  EXPECTED_ASSET_NAMES,
  LIGHTING_AND_WARDROBE,
  RENDER_SCRIPT_RELATIVE_PATH,
  RISK_NOTES
} from "./content";

const REPO_ROOT = path.resolve(process.cwd(), "..", "..");
const ASSET_ROOT = path.join(REPO_ROOT, "docs", "capture_guides", "assets");
const GUIDE_DOC_PATH = path.join(REPO_ROOT, DOCS_GUIDE_RELATIVE_PATH);

async function fileExists(filePath: string) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

export default async function CaptureGuidePage() {
  const docsGuideExists = await fileExists(GUIDE_DOC_PATH);
  const assetChecks = await Promise.all(
    EXPECTED_ASSET_NAMES.map(async (fileName) => ({
      exists: await fileExists(path.join(ASSET_ROOT, fileName)),
      fileName
    }))
  );
  const assetStatus = new Map(assetChecks.map((entry) => [entry.fileName, entry.exists]));
  const availableAssetCount = assetChecks.filter((entry) => entry.exists).length;
  const missingAssetNames = assetChecks
    .filter((entry) => !entry.exists)
    .map((entry) => entry.fileName);

  return (
    <StudioFrame currentPath="/studio/capture-guide" phaseLabel="Phase 08">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">capture guidance</span>
        <span className="statusBadge">
          {missingAssetNames.length === 0
            ? `${availableAssetCount} Blender assets ready`
            : `${missingAssetNames.length} Blender assets missing`}
        </span>
        <span className="statusBadge">
          {docsGuideExists ? "guide markdown ready" : "guide markdown missing"}
        </span>
      </div>

      <PageHeader
        eyebrow="Phase 08"
        title="Capture guide"
        summary="Photograph the subject like a controlled sweep: front, left, right, back, three-quarter, then a dedicated head pass. LoRA can start with a smaller set, but the later high-detail 3D phases need a much larger photo set up front."
        actions={<span className="headerCallout">LoRA: 20-30 photos. High-detail 3D: 60-120+ photos.</span>}
      />

      {missingAssetNames.length > 0 ? (
        <div className="captureGuideAlert" role="alert">
          Missing assets: {missingAssetNames.join(", ")}
        </div>
      ) : null}

      <div className="studioPanelGrid">
        <SectionCard
          title="Shot count and distance"
          description="These numbers are the working baseline for honest onboarding guidance."
        >
          <KeyValueList items={[...CAPTURE_REQUIREMENTS]} />
        </SectionCard>

        <SectionCard
          title="How to shoot"
          description="Keep the capture repeatable so later QC and reconstruction have stable input."
        >
          <ul className="captureGuideList">
            {CAPTURE_STEPS.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard
          title="Lighting and wardrobe"
          description="Good light and readable edges matter more than fashionable styling in this step."
        >
          <ul className="captureGuideList">
            {LIGHTING_AND_WARDROBE.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard
          title="Backgrounds to avoid"
          description="Remove visual clutter that competes with the body outline or face landmarks."
        >
          <ul className="captureGuideList">
            {BACKGROUNDS_TO_AVOID.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </SectionCard>
      </div>

      <SectionCard
        title="High-detail 3D warning"
        description="This note is intentionally early and explicit so users do not undershoot the photo count."
      >
        <ul className="captureGuideList">
          {RISK_NOTES.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </SectionCard>

      <section className="captureGuideGallery" aria-label="Capture reference boards">
        {CAPTURE_ASSET_GROUPS.map((group) => (
          <SectionCard key={group.title} title={group.title} description={group.description}>
            <div className="captureGuideAssetGrid">
              {group.assets.map((asset) => {
                const isAvailable = assetStatus.get(asset.fileName) === true;

                return (
                  <figure key={asset.fileName} className="captureGuideFigure">
                    {isAvailable ? (
                      <Image
                        src={`/studio/capture-guide/assets/${asset.fileName}`}
                        alt={asset.alt}
                        width={768}
                        height={768}
                        unoptimized
                      />
                    ) : (
                      <div className="captureGuideFigureFallback">Missing asset</div>
                    )}
                    <figcaption>
                      <strong>{asset.fileName}</strong>
                      <span>{asset.caption}</span>
                    </figcaption>
                  </figure>
                );
              })}
            </div>
          </SectionCard>
        ))}
      </section>

      <SectionCard
        title="Tracked deliverables"
        description="These files are part of the Phase 08 contract and can be re-generated locally."
      >
        <div className="fileTileGrid">
          <FileTile
            fileName="capture_guide.md"
            filePath={DOCS_GUIDE_RELATIVE_PATH}
            description={
              docsGuideExists
                ? "Concrete markdown instructions for the same onboarding flow shown on this route."
                : "Missing markdown guide; the route is reporting that truthfully."
            }
          />
          <FileTile
            fileName="render_capture_guides.sh"
            filePath={RENDER_SCRIPT_RELATIVE_PATH}
            description="Shell entrypoint that re-renders the Blender onboarding boards into docs/capture_guides/assets."
          />
          <FileTile
            fileName="render_capture_guides.py"
            filePath={BLENDER_SCRIPT_RELATIVE_PATH}
            description="Blender 4.5 LTS script that builds the neutral mannequin boards and head close-ups."
          />
          <FileTile
            fileName="assets/"
            filePath={ASSET_DIRECTORY_RELATIVE_PATH}
            description={`${availableAssetCount} rendered PNG assets currently available in the tracked guide directory.`}
          />
        </div>
      </SectionCard>
    </StudioFrame>
  );
}
