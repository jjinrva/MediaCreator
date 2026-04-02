import React from "react";

type BodyParameterCatalogEntry = {
  default_value: number;
  display_label: string;
  group: string;
  key: string;
  max_value: number;
  min_value: number;
  step: number;
  unit: string;
};

type BodyParameterReadoutProps = {
  catalog: BodyParameterCatalogEntry[];
  currentValues: Record<string, number>;
};

function formatValue(value: number, unit: string) {
  const rendered = value.toFixed(2);
  return unit ? `${rendered}${unit}` : rendered;
}

export function BodyParameterReadout({
  catalog,
  currentValues
}: BodyParameterReadoutProps) {
  return (
    <div className="fileTileGrid">
      {catalog.map((entry) => (
        <article key={entry.key} className="fileTile">
          <div className="fileTileHeader">
            <strong>{entry.display_label}</strong>
            <code>{entry.key}</code>
          </div>
          <span>{formatValue(currentValues[entry.key] ?? entry.default_value, entry.unit)}</span>
          <span>{`Group: ${entry.group}`}</span>
          <span>{`Range: ${entry.min_value}${entry.unit} to ${entry.max_value}${entry.unit}`}</span>
        </article>
      ))}
    </div>
  );
}
