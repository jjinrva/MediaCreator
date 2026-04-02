from datetime import datetime

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDIdentityMixin


class ServiceHeartbeat(UUIDIdentityMixin, TimestampMixin, Base):
    __tablename__ = "service_heartbeats"

    service_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    detail: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        server_default=text("'polling'"),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
