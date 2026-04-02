import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FaceParameterEditor } from "../../components/face-editor/FaceParameterEditor";

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

describe("Phase 16 face parameter editor", () => {
  it("renders sliders, numeric outputs, and tooltip triggers from facial metadata", () => {
    render(
      <FaceParameterEditor
        characterPublicId="phase-16-character"
        initialCatalog={[
          {
            default_value: 0,
            display_label: "Jaw open",
            group: "mouth",
            help_text: "Controls jaw opening.",
            key: "jaw_open",
            max_value: 1,
            min_value: 0,
            shape_key_name: "JawOpen",
            step: 0.01,
            unit: "x"
          },
          {
            default_value: 1,
            display_label: "Neutral blend",
            group: "base",
            help_text: "Controls neutral blending.",
            key: "neutral_expression_blend",
            max_value: 1,
            min_value: 0,
            shape_key_name: "NeutralExpression",
            step: 0.01,
            unit: "x"
          }
        ]}
        initialValues={{
          jaw_open: 0,
          neutral_expression_blend: 1
        }}
      />
    );

    expect(screen.getByRole("slider", { name: "Jaw open" })).toBeTruthy();
    expect(screen.getByRole("slider", { name: "Neutral blend" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Jaw open" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Neutral blend" })).toBeTruthy();
    expect(screen.getByText("0.00x")).toBeTruthy();
    expect(screen.getByText("1.00x")).toBeTruthy();
  });
});
