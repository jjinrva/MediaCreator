import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.jobs import JobDetailResponse
from app.services.jobs import get_job_by_public_id

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("/{job_public_id}", response_model=JobDetailResponse)
def read_job(
    job_public_id: uuid.UUID,
    session: Session = Depends(get_db_session),
) -> JobDetailResponse:
    job = get_job_by_public_id(session, job_public_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return JobDetailResponse.model_validate(job)
