import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PoseParameterEditor } from "../../components/pose-editor/PoseParameterEditor";

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

describe("Phase 15 pose parameter editor", () => {
  it("renders sliders, numeric outputs, and tooltip triggers from pose metadata", () => {
    render(
      <PoseParameterEditor
        characterPublicId="phase-15-character"
        initialCatalog={[
          {
            axis: "x",
            bone_name: "upper_arm.L",
            default_value: 0,
            display_label: "Left arm raise",
            group: "arms",
            help_text: "Raises the left arm.",
            key: "upper_arm_l_pitch_deg",
            max_value: 90,
            min_value: -45,
            step: 1,
            unit: "deg"
          },
          {
            axis: "x",
            bone_name: "thigh.R",
            default_value: 0,
            display_label: "Right leg raise",
            group: "legs",
            help_text: "Raises the right leg.",
            key: "thigh_r_pitch_deg",
            max_value: 75,
            min_value: -35,
            step: 1,
            unit: "deg"
          }
        ]}
        initialValues={{
          thigh_r_pitch_deg: 0,
          upper_arm_l_pitch_deg: 0
        }}
      />
    );

    expect(screen.getByRole("slider", { name: "Left arm raise" })).toBeTruthy();
    expect(screen.getByRole("slider", { name: "Right leg raise" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Left arm raise" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "More info about Right leg raise" })).toBeTruthy();
    expect(screen.getAllByText("0deg")).toHaveLength(2);
  });
});
