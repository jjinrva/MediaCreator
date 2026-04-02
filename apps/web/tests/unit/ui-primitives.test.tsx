import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import StudioPage from "../../app/studio/page";
import { EmptyState } from "../../components/ui/EmptyState";
import { FileTile } from "../../components/ui/FileTile";
import { HistoryList } from "../../components/ui/HistoryList";
import { KeyValueList } from "../../components/ui/KeyValueList";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionCard } from "../../components/ui/SectionCard";

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

Object.defineProperty(window, "ResizeObserver", {
  configurable: true,
  writable: true,
  value: ResizeObserverStub
});

describe("Phase 07 UI primitives", () => {
  it("renders the shared shell primitives without fake data", () => {
    render(
      <SectionCard title="Primitive harness" description="Shared building blocks">
        <PageHeader
          eyebrow="Harness"
          title="Studio primitives"
          summary="Shared shell components."
        />
        <KeyValueList items={[{ label: "Mode", value: "Single-user rebuild" }]} />
        <HistoryList items={[{ label: "Phase 06", detail: "Capability checks passed." }]} />
        <FileTile
          fileName="text_to_image_v1.json"
          filePath="workflows/comfyui/text_to_image_v1.json"
          description="Workflow contract."
        />
        <EmptyState
          title="No generated assets"
          description="Generation remains gated until later verified phases."
        />
      </SectionCard>
    );

    expect(screen.getByRole("heading", { name: "Primitive harness" })).toBeTruthy();
    expect(screen.getByText("Studio primitives")).toBeTruthy();
    expect(screen.getByText("Single-user rebuild")).toBeTruthy();
    expect(screen.getByText("Capability checks passed.")).toBeTruthy();
    expect(screen.getByText("text_to_image_v1.json")).toBeTruthy();
    expect(screen.getByText("No generated assets")).toBeTruthy();
  });

  it("shows adjacent info tooltips for every visible phase 07 input", () => {
    render(<StudioPage />);

    const controlsTab = screen.getByRole("tab", { name: "Shell controls" });
    fireEvent.click(controlsTab);

    expect(screen.getByRole("slider", { name: "Layout focus" })).toBeTruthy();
    expect(screen.getByRole("textbox", { name: "Workspace label" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Layout focus" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Workspace label" })).toBeTruthy();
  });
});
