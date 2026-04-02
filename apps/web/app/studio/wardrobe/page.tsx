/* eslint-disable @next/next/no-img-element */

import React from "react";

import { WardrobeCatalog } from "../../../components/wardrobe-catalog/WardrobeCatalog";
import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";

type WardrobeCatalogPayload = {
  generation_capability: {
    detail: string;
    missing_requirements: string[];
    status: string;
  };
  items: Array<{
    base_color: string;
    creation_path: string;
    fitting_status: string;
    garment_type: string;
    history: Array<{
      created_at: string;
      details: Record<string, unknown>;
      event_type: string;
      public_id: string;
    }>;
    label: string;
    material: string;
    prompt_text: string | null;
    public_id: string;
    source_photo_url: string | null;
    status: string;
  }>;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

async function getWardrobeCatalog(): Promise<WardrobeCatalogPayload> {
  const response = await fetch(`${API_BASE_URL}/api/v1/wardrobe`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to load the wardrobe catalog.");
  }

  return (await response.json()) as WardrobeCatalogPayload;
}

export default async function WardrobePage() {
  const wardrobeCatalog = await getWardrobeCatalog();

  return (
    <StudioFrame currentPath="/studio/wardrobe" phaseLabel="Phase 22">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">closet catalog</span>
        <span className="statusBadge">material metadata</span>
        <span className="statusBadge">truthful AI path</span>
      </div>

      <PageHeader
        eyebrow="Phase 22"
        title="Wardrobe catalog"
        summary="Create reusable closet items from one garment photo or an AI prompt-backed request. Material, color, and fitting data are tracked separately from the base wardrobe asset."
        actions={<span className="headerCallout">{`${wardrobeCatalog.items.length} item(s)`}</span>}
      />

      <SectionCard
        title="Closet"
        description="Phase 22 stores real wardrobe assets only. Photo ingest writes a source artifact, and the AI path keeps prompt-backed entries truthful about ComfyUI readiness."
      >
        <WardrobeCatalog
          generationCapability={{
            detail: wardrobeCatalog.generation_capability.detail,
            missingRequirements: wardrobeCatalog.generation_capability.missing_requirements,
            status: wardrobeCatalog.generation_capability.status
          }}
          items={wardrobeCatalog.items.map((item) => ({
            baseColor: item.base_color,
            creationPath: item.creation_path,
            fittingStatus: item.fitting_status,
            garmentType: item.garment_type,
            history: item.history.map((event) => ({
              createdAt: event.created_at,
              eventType: event.event_type,
              publicId: event.public_id
            })),
            label: item.label,
            material: item.material,
            promptText: item.prompt_text,
            publicId: item.public_id,
            sourcePhotoUrl: item.source_photo_url,
            status: item.status
          }))}
        />
      </SectionCard>
    </StudioFrame>
  );
}
