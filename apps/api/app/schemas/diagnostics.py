from pydantic import BaseModel


class DiagnosticCheckResponse(BaseModel):
    check_id: str
    detail: str
    label: str
    status: str


class FinalVerifyReportSummaryResponse(BaseModel):
    generated_at: str | None
    human_report_path: str
    machine_report_path: str
    overall_status: str | None


class DiagnosticsResponse(BaseModel):
    checks: list[DiagnosticCheckResponse]
    report_summary: FinalVerifyReportSummaryResponse | None
