import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { BodyParameterEditor } from "../../components/body-editor/BodyParameterEditor";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh
  })
}));

class ResizeObserverMock {
  disconnect() {}
  observe() {}
  unobserve() {}
}

Object.defineProperty(globalThis, "ResizeObserver", {
  configurable: true,
  value: ResizeObserverMock
});

describe("Phase 14 body parameter editor", () => {
  it("renders sliders, numeric outputs, and tooltip triggers from backend metadata", () => {
    render(
      <BodyParameterEditor
        characterPublicId="phase-14-character"
        initialCatalog={[
          {
            default_value: 1,
            display_label: "Height scale",
            group: "overall",
            help_text: "Scales the overall body height.",
            key: "height_scale",
            max_value: 1.15,
            min_value: 0.85,
            step: 0.01,
            unit: "x"
          },
          {
            default_value: 1,
            display_label: "Shoulder width",
            group: "torso",
            help_text: "Controls the width of the shoulders.",
            key: "shoulder_width",
            max_value: 1.2,
            min_value: 0.8,
            step: 0.01,
            unit: "x"
          }
        ]}
        initialValues={{
          height_scale: 1,
          shoulder_width: 1
        }}
      />
    );

    expect(screen.getByRole("slider", { name: "Height scale" })).toBeTruthy();
    expect(screen.getByRole("slider", { name: "Shoulder width" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Height scale" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Shoulder width" })).toBeTruthy();
    expect(screen.getAllByText("1.00x")).toHaveLength(2);
  });
});
