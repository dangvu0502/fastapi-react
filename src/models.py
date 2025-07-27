from datetime import datetime, timezone

from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime


class TimeStampMixin:
    """Timestamping mixin for created_at and updated_at fields."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    @staticmethod
    def _updated_at(mapper, connection, target):
        """Updates the updated_at field to the current UTC time."""
        target.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    @classmethod
    def __declare_last__(cls):
        """Registers the before_update event to update the updated_at field."""
        event.listen(cls, "before_update", cls._updated_at)
