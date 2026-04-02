import React from "react";

import { PageHeader } from "../../../components/ui/PageHeader";
import { SectionCard } from "../../../components/ui/SectionCard";
import { StudioFrame } from "../../../components/ui/StudioFrame";
import { DiagnosticsPanel } from "./DiagnosticsPanel";

type DiagnosticsPayload = {
  checks: Array<{
    check_id: string;
    detail: string;
    label: string;
    status: string;
  }>;
  report_summary: {
    generated_at: string | null;
    human_report_path: string;
    machine_report_path: string;
    overall_status: string | null;
  } | null;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL ?? "http://10.0.0.102:8010";

async function getDiagnostics(): Promise<DiagnosticsPayload> {
  const response = await fetch(`${API_BASE_URL}/api/v1/system/diagnostics`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Unable to load the diagnostics screen.");
  }
  return (await response.json()) as DiagnosticsPayload;
}

function countByStatus(
  checks: DiagnosticsPayload["checks"],
  status: string
): number {
  return checks.filter((check) => check.status === status).length;
}

export default async function DiagnosticsPage() {
  const payload = await getDiagnostics();

  return (
    <StudioFrame currentPath="/studio/diagnostics" phaseLabel="Phase 26">
      <div className="statusStrip" role="status" aria-live="polite">
        <span className="statusBadge">{`${countByStatus(payload.checks, "pass")} pass`}</span>
        <span className="statusBadge">{`${countByStatus(payload.checks, "fail")} fail`}</span>
        <span className="statusBadge">{`${countByStatus(payload.checks, "not-run")} not-run`}</span>
      </div>

      <PageHeader
        eyebrow="Phase 26"
        title="Diagnostics"
        summary="Run the current end-to-end checks for ingest, persistent editing, preview/export availability, LoRA training readiness, and generation workflow readiness without hiding failures."
        actions={<span className="headerCallout">{`${payload.checks.length} live checks`}</span>}
      />

      <SectionCard
        title="Live diagnostic checks"
        description="These checks reflect the current persisted state. A fail means the runtime is missing that capability right now, not that the UI invented a broken state."
      >
        <DiagnosticsPanel
          checks={payload.checks.map((check) => ({
            checkId: check.check_id,
            detail: check.detail,
            label: check.label,
            status: check.status
          }))}
          reportSummary={
            payload.report_summary
              ? {
                  generatedAt: payload.report_summary.generated_at,
                  humanReportPath: payload.report_summary.human_report_path,
                  machineReportPath: payload.report_summary.machine_report_path,
                  overallStatus: payload.report_summary.overall_status
                }
              : null
          }
        />
      </SectionCard>
    </StudioFrame>
  );
}
