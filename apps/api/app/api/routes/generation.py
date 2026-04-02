from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.generation import (
    CreateGenerationRequestRequest,
    ExternalLoraSearchResponse,
    GenerationRequestRecordResponse,
    GenerationWorkspaceResponse,
    ImportExternalLoraRequest,
    PromptExpansionRequest,
    PromptExpansionResponse,
)
from app.services.prompt_expansion import (
    create_generation_request,
    expand_prompt_text,
    get_civitai_import_capability,
    get_generation_workspace_payload,
    import_external_lora,
    search_external_loras,
)

router = APIRouter(prefix="/api/v1/generation", tags=["generation"])


@router.get("", response_model=GenerationWorkspaceResponse)
def get_generation_workspace(
    db_session: Session = Depends(get_db_session),
) -> GenerationWorkspaceResponse:
    payload = get_generation_workspace_payload(db_session)
    return GenerationWorkspaceResponse.model_validate(payload)


@router.post("/expand", response_model=PromptExpansionResponse)
def expand_prompt(
    body: PromptExpansionRequest,
    db_session: Session = Depends(get_db_session),
) -> PromptExpansionResponse:
    payload = expand_prompt_text(db_session, body.prompt_text)
    return PromptExpansionResponse.model_validate(payload)


@router.post(
    "/requests",
    response_model=GenerationRequestRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_generation_request_route(
    body: CreateGenerationRequestRequest,
    db_session: Session = Depends(get_db_session),
) -> GenerationRequestRecordResponse:
    try:
        with db_session.begin():
            payload = create_generation_request(
                db_session,
                external_lora_registry_public_id=body.external_lora_registry_public_id,
                local_lora_registry_public_id=body.local_lora_registry_public_id,
                prompt_text=body.prompt_text,
                target_kind=body.target_kind,
            )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return GenerationRequestRecordResponse.model_validate(payload)


@router.get("/external-loras/search", response_model=ExternalLoraSearchResponse)
def search_external_loras_route(
    q: str = Query(min_length=1),
    db_session: Session = Depends(get_db_session),
) -> ExternalLoraSearchResponse:
    del db_session
    capability = get_civitai_import_capability()
    if capability["status"] != "enabled":
        return ExternalLoraSearchResponse(
            results=[],
            status=str(capability["status"]),
        )

    try:
        results = search_external_loras(q)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ExternalLoraSearchResponse.model_validate({"results": results, "status": "enabled"})


@router.post("/external-loras/import", response_model=GenerationWorkspaceResponse)
def import_external_lora_route(
    body: ImportExternalLoraRequest,
    db_session: Session = Depends(get_db_session),
) -> GenerationWorkspaceResponse:
    capability = get_civitai_import_capability()
    if capability["status"] != "enabled":
        raise HTTPException(status_code=400, detail=str(capability["detail"]))

    try:
        with db_session.begin():
            import_external_lora(
                db_session,
                download_url=body.download_url,
                model_name=body.model_name,
                prompt_handle=body.prompt_handle,
            )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db_session.expire_all()
    payload = get_generation_workspace_payload(db_session)
    return GenerationWorkspaceResponse.model_validate(payload)
