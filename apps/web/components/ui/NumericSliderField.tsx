"use client";

import * as Slider from "@radix-ui/react-slider";
import React from "react";

import { InfoTooltip } from "./InfoTooltip";
import type { FieldMetadata } from "./field-metadata";

type NumericSliderFieldProps = {
  field: FieldMetadata & {
    min: number;
    max: number;
    step: number;
    suffix?: string;
  };
  value: number;
  onChange: (value: number) => void;
  onCommit?: (value: number) => void;
};

function formatValue(value: number, step: number) {
  const decimals = step.toString().includes(".")
    ? step.toString().split(".")[1]?.length ?? 0
    : 0;

  return value.toFixed(decimals);
}

export function NumericSliderField({
  field,
  value,
  onChange,
  onCommit
}: NumericSliderFieldProps) {
  const renderedValue = field.suffix
    ? `${formatValue(value, field.step)}${field.suffix}`
    : formatValue(value, field.step);

  return (
    <div className="fieldStack">
      <div className="fieldHeader">
        <label id={`${field.id}-label`} htmlFor={field.id} className="fieldLabel">
          {field.label}
        </label>
        <InfoTooltip content={field.helpText} label={field.label} />
      </div>
      <div className="sliderRow">
        <Slider.Root
          id={field.id}
          className="sliderRoot"
          min={field.min}
          max={field.max}
          step={field.step}
          value={[value]}
          onValueChange={(nextValue) => onChange(nextValue[0] ?? value)}
          onValueCommit={(nextValue) => onCommit?.(nextValue[0] ?? value)}
          aria-labelledby={`${field.id}-label`}
        >
          <Slider.Track className="sliderTrack">
            <Slider.Range className="sliderRange" />
          </Slider.Track>
          <Slider.Thumb className="sliderThumb" aria-label={field.label} />
        </Slider.Root>
        <output className="sliderValue" htmlFor={field.id}>
          {renderedValue}
        </output>
      </div>
    </div>
  );
}
