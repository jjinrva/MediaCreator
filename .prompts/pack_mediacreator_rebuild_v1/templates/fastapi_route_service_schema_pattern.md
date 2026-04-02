
# FastAPI route / schema / service split

```py
# route
@router.patch("/{public_id}/body")
def update_body_values(
    public_id: str,
    payload: CharacterBodyUpdateRequest,
    session: Session = Depends(get_session),
):
    character = body_service.update_character_body(
        session=session,
        public_id=public_id,
        updates=payload.updates,
    )
    return CharacterBodyUpdateResponse.model_validate(character, from_attributes=True)
```

```py
# service
def update_character_body(*, session: Session, public_id: str, updates: list[BodyUpdate]) -> Character:
    character = get_character_by_public_id(session, public_id)
    apply_body_updates(session=session, character=character, updates=updates)
    write_history_event(...)
    session.commit()
    session.refresh(character)
    return character
```
