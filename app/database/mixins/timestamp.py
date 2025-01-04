"""
Adding this SQLModel mixin will add created_at, updated_at, and deleted_at to your tables.
`created_at` will auto-populate upon creation. `updated_at` will do the right thing on updates.
Usage:
    class YourModel(TimestampMixin):
        ...
At this point all classes inheriting from YourModel will have the usual fields added.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import DateTime, Field, SQLModel


def custom_encoder(obj):
    """Optional. Useful for serializing the date as a string when dumping to JSON:
    >>> json.dumps(obj, default=custom_encoder)
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


class TimestampMixin(SQLModel):
    """Mixin class for timestamp fields."""

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Database timestamp when the record was created.",
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(),
        description="Database timestamp when the record was deleted.",
    )
