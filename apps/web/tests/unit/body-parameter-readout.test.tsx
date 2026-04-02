import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BodyParameterReadout } from "../../components/body-editor/BodyParameterReadout";

describe("Phase 13 body parameter readout", () => {
  it("renders catalog labels, stable keys, and current numeric values", () => {
    render(
      <BodyParameterReadout
        catalog={[
          {
            default_value: 1,
            display_label: "Height scale",
            group: "overall",
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
            key: "shoulder_width",
            max_value: 1.2,
            min_value: 0.8,
            step: 0.01,
            unit: "x"
          }
        ]}
        currentValues={{
          height_scale: 1,
          shoulder_width: 1.08
        }}
      />
    );

    expect(screen.getByText("Height scale")).toBeTruthy();
    expect(screen.getByText("height_scale")).toBeTruthy();
    expect(screen.getByText("1.08x")).toBeTruthy();
    expect(screen.getByText("Group: torso")).toBeTruthy();
  });
});
