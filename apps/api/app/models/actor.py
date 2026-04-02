import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDIdentityMixin


class Actor(UUIDIdentityMixin, TimestampMixin, Base):
    __tablename__ = "actors"

    handle: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    current_owner_actor_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
