"use client";

import React from "react";
import { useRouter } from "next/navigation";

export type DiagnosticCheck = {
  checkId: string;
  detail: string;
  label: string;
  status: string;
};

export type FinalVerifyReportSummary = {
  generatedAt: string | null;
  humanReportPath: string;
  machineReportPath: string;
  overallStatus: string | null;
};

type DiagnosticsPanelProps = {
  checks: DiagnosticCheck[];
  reportSummary: FinalVerifyReportSummary | null;
};

function statusClassName(status: string): string {
  if (status === "pass" || status === "ready") {
    return "runtimeStatusChip runtimeStatusChipReady";
  }
  if (status === "fail" || status === "missing" || status === "unavailable") {
    return "runtimeStatusChip runtimeStatusChipFail";
  }
  return "runtimeStatusChip runtimeStatusChipWarn";
}

export function DiagnosticsPanel({ checks, reportSummary }: DiagnosticsPanelProps) {
  const router = useRouter();
  const [isPending, startTransition] = React.useTransition();

  return (
    <div className="diagnosticsLayout">
      <div className="diagnosticsToolbar">
        <p>Failing checks are current truth, not placeholders. Re-run to refresh against live data.</p>
        <button
          type="button"
          className="diagnosticActionButton"
          onClick={() => startTransition(() => router.refresh())}
          disabled={isPending}
        >
          {isPending ? "Running diagnostics..." : "Run diagnostics again"}
        </button>
      </div>

      <ol className="diagnosticsList">
        {checks.map((check) => (
          <li key={check.checkId} className="diagnosticItem">
            <div className="diagnosticItemHeader">
              <div>
                <h3>{check.label}</h3>
                <p>{check.detail}</p>
              </div>
              <span className={statusClassName(check.status)}>{check.status}</span>
            </div>
          </li>
        ))}
      </ol>

      {reportSummary ? (
        <section className="runtimePanel">
          <div className="runtimePanelHeader">
            <div>
              <h3>Latest full verify sweep</h3>
              <p>The final verification matrix is recorded separately from the live diagnostic pass.</p>
            </div>
            <span className={statusClassName(reportSummary.overallStatus ?? "not-run")}>
              {reportSummary.overallStatus ?? "not-run"}
            </span>
          </div>
          <dl className="runtimeMetaList">
            <div className="runtimeMetaRow">
              <dt>Generated at</dt>
              <dd>{reportSummary.generatedAt ?? "not recorded"}</dd>
            </div>
            <div className="runtimeMetaRow">
              <dt>Human report</dt>
              <dd>{reportSummary.humanReportPath}</dd>
            </div>
            <div className="runtimeMetaRow">
              <dt>Machine report</dt>
              <dd>{reportSummary.machineReportPath}</dd>
            </div>
          </dl>
        </section>
      ) : (
        <section className="runtimePanel">
          <div className="runtimePanelHeader">
            <div>
              <h3>Latest full verify sweep</h3>
              <p>No final verification sweep has been recorded yet for this runtime.</p>
            </div>
            <span className={statusClassName("not-run")}>not-run</span>
          </div>
        </section>
      )}
    </div>
  );
}
