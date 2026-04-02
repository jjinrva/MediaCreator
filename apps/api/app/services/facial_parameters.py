from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.facial_parameters import FACIAL_PARAMETER_CATALOG, FacialParameter
from app.models.history_event import HistoryEvent
from app.services.jobs import get_system_actor_id


def _facial_parameter_query() -> Select[tuple[FacialParameter]]:
    return select(FacialParameter).order_by(FacialParameter.created_at.asc())


def _character_asset_query() -> Select[tuple[Asset]]:
    return select(Asset).order_by(Asset.created_at.asc())


FACIAL_PARAMETER_CATALOG_BY_KEY = {
    definition.key: definition for definition in FACIAL_PARAMETER_CATALOG
}


def initialize_facial_parameter_rows(session: Session, character_asset_id: uuid.UUID) -> None:
    existing_keys = set(
        session.scalars(
            select(FacialParameter.parameter_key).where(
                FacialParameter.character_asset_id == character_asset_id
            )
        ).all()
    )

    for definition in FACIAL_PARAMETER_CATALOG:
        if definition.key in existing_keys:
            continue

        session.add(
            FacialParameter(
                character_asset_id=character_asset_id,
                parameter_key=definition.key,
                numeric_value=definition.default_value,
            )
        )

    session.flush()


def get_character_facial_parameter_payload(
    session: Session,
    character_public_id: uuid.UUID,
) -> dict[str, object] | None:
    character_asset = session.execute(
        _character_asset_query().where(
            Asset.public_id == character_public_id,
            Asset.asset_type == "character",
        )
    ).scalar_one_or_none()
    if character_asset is None:
        return None

    stored_values = {
        row.parameter_key: row.numeric_value
        for row in session.scalars(
            _facial_parameter_query().where(
                FacialParameter.character_asset_id == character_asset.id
            )
        ).all()
    }

    return {
        "character_public_id": character_asset.public_id,
        "catalog": [
            {
                "key": definition.key,
                "display_label": definition.display_label,
                "group": definition.group,
                "shape_key_name": definition.shape_key_name,
                "min_value": definition.min_value,
                "max_value": definition.max_value,
                "step": definition.step,
                "unit": definition.unit,
                "default_value": definition.default_value,
                "help_text": definition.help_text,
            }
            for definition in FACIAL_PARAMETER_CATALOG
        ],
        "current_values": {
            definition.key: float(stored_values.get(definition.key, definition.default_value))
            for definition in FACIAL_PARAMETER_CATALOG
        },
    }


def update_character_facial_parameter(
    session: Session,
    character_public_id: uuid.UUID,
    *,
    numeric_value: float,
    parameter_key: str,
) -> dict[str, object]:
    character_asset = session.execute(
        _character_asset_query().where(
            Asset.public_id == character_public_id,
            Asset.asset_type == "character",
        )
    ).scalar_one_or_none()
    if character_asset is None:
        raise LookupError("Character not found.")

    definition = FACIAL_PARAMETER_CATALOG_BY_KEY.get(parameter_key)
    if definition is None:
        raise ValueError("Unknown facial parameter key.")
    if not definition.min_value <= numeric_value <= definition.max_value:
        raise ValueError("Facial parameter value is outside the allowed range.")

    facial_parameter = session.execute(
        _facial_parameter_query().where(
            FacialParameter.character_asset_id == character_asset.id,
            FacialParameter.parameter_key == parameter_key,
        )
    ).scalar_one_or_none()

    if facial_parameter is None:
        facial_parameter = FacialParameter(
            character_asset_id=character_asset.id,
            parameter_key=parameter_key,
            numeric_value=definition.default_value,
        )
        session.add(facial_parameter)
        session.flush()

    previous_value = facial_parameter.numeric_value
    facial_parameter.numeric_value = numeric_value

    if previous_value != numeric_value:
        actor_id = get_system_actor_id(session)
        session.add(
            HistoryEvent(
                actor_id=actor_id,
                asset_id=character_asset.id,
                event_type="face.parameter_updated",
                details={
                    "catalog_version": "face-v1",
                    "display_label": definition.display_label,
                    "numeric_value": numeric_value,
                    "parameter_key": parameter_key,
                    "previous_value": previous_value,
                    "shape_key_name": definition.shape_key_name,
                },
            )
        )

    session.flush()
    payload = get_character_facial_parameter_payload(session, character_public_id)
    if payload is None:  # pragma: no cover - guarded by the same transaction above
        raise LookupError("Character not found.")
    return payload
