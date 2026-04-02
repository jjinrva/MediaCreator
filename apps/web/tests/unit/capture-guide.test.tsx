import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import CaptureGuidePage from "../../app/studio/capture-guide/page";
import { EXPECTED_ASSET_NAMES } from "../../app/studio/capture-guide/content";

describe("Phase 08 capture guide", () => {
  it("renders concrete onboarding instructions and the real rendered asset references", async () => {
    render(await CaptureGuidePage());

    expect(screen.getByRole("heading", { name: "Capture guide" })).toBeTruthy();
    expect(screen.getByText(/20-30 sharp photos/i)).toBeTruthy();
    expect(screen.getByText(/60-120\+ sharp photos/i)).toBeTruthy();
    expect(screen.getByText(/3-4 meters/i)).toBeTruthy();
    expect(screen.getByText(/0.8-1.2 meters/i)).toBeTruthy();
    expect(screen.getByText(/60-70% overlap/i)).toBeTruthy();
    expect(screen.getByText(/arms 10-15 cm away from the torso/i)).toBeTruthy();
    expect(screen.getByText(/hairline stays visible/i)).toBeTruthy();
    expect(screen.getByText("docs/capture_guides/capture_guide.md")).toBeTruthy();
    expect(screen.getByRole("img", { name: "Male mannequin full-body front reference" })).toBeTruthy();
    expect(screen.getByRole("img", { name: "Female mannequin front head reference" })).toBeTruthy();
    expect(screen.getAllByRole("img")).toHaveLength(EXPECTED_ASSET_NAMES.length);
  });
});
