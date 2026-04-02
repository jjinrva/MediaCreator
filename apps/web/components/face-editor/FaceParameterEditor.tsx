"use client";

import { useRouter } from "next/navigation";
import React from "react";

import { NumericSliderField } from "../ui/NumericSliderField";

type FacialParameterCatalogEntry = {
  default_value: number;
  display_label: string;
  group: string;
  help_text: string;
  key: string;
  max_value: number;
  min_value: number;
  shape_key_name: string;
  step: number;
  unit: string;
};

type FaceParameterEditorProps = {
  characterPublicId: string;
  initialCatalog: FacialParameterCatalogEntry[];
  initialValues: Record<string, number>;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

function formatValue(value: number, unit: string) {
  return `${value.toFixed(2)}${unit}`;
}

export function FaceParameterEditor({
  characterPublicId,
  initialCatalog,
  initialValues
}: FaceParameterEditorProps) {
  const router = useRouter();
  const [canonicalValues, setCanonicalValues] = React.useState(initialValues);
  const [draftValues, setDraftValues] = React.useState(initialValues);
  const [error, setError] = React.useState<string | null>(null);
  const [saveSummary, setSaveSummary] = React.useState<string | null>(null);

  React.useEffect(() => {
    setCanonicalValues(initialValues);
    setDraftValues(initialValues);
  }, [initialValues]);

  async function handleCommit(parameterKey: string, numericValue: number, label: string, unit: string) {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/api/v1/face/characters/${characterPublicId}`, {
        body: JSON.stringify({
          parameter_key: parameterKey,
          numeric_value: numericValue
        }),
        headers: {
          "content-type": "application/json"
        },
        method: "PUT"
      });

      if (!response.ok) {
        throw new Error("Face parameter save failed.");
      }

      const payload = (await response.json()) as { current_values: Record<string, number> };
      setCanonicalValues(payload.current_values);
      setDraftValues(payload.current_values);
      setSaveSummary(
        `Saved ${label} at ${formatValue(payload.current_values[parameterKey], unit)}. History updated from the API.`
      );
      router.refresh();
    } catch {
      setDraftValues(canonicalValues);
      setError("Face parameter save failed before the canonical state could reload.");
    }
  }

  return (
    <div className="characterImportMain">
      {initialCatalog.map((entry) => (
        <NumericSliderField
          key={entry.key}
          field={{
            id: `face-${entry.key}`,
            label: entry.display_label,
            helpText: entry.help_text,
            min: entry.min_value,
            max: entry.max_value,
            step: entry.step,
            suffix: entry.unit
          }}
          value={draftValues[entry.key] ?? entry.default_value}
          onChange={(value) => {
            setDraftValues((currentValues) => ({
              ...currentValues,
              [entry.key]: value
            }));
            setSaveSummary(null);
          }}
          onCommit={(value) => {
            void handleCommit(entry.key, value, entry.display_label, entry.unit);
          }}
        />
      ))}

      {error ? (
        <p className="captureGuideAlert" role="alert">
          {error}
        </p>
      ) : null}

      {saveSummary ? (
        <p className="characterImportSummary" role="status">
          {saveSummary}
        </p>
      ) : null}
    </div>
  );
}
