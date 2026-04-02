from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.diagnostics import DiagnosticsResponse
from app.schemas.system import SystemStatusResponse
from app.services.diagnostics import get_live_diagnostics_payload
from app.services.system_runtime import get_system_settings_payload

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status", response_model=SystemStatusResponse)
def read_system_status(
    db_session: Session = Depends(get_db_session),
) -> SystemStatusResponse:
    return SystemStatusResponse.model_validate(get_system_settings_payload(db_session))


@router.get("/diagnostics", response_model=DiagnosticsResponse)
def read_system_diagnostics(
    db_session: Session = Depends(get_db_session),
) -> DiagnosticsResponse:
    return DiagnosticsResponse.model_validate(get_live_diagnostics_payload(db_session))
