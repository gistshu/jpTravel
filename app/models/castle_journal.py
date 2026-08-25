from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, TimestampMixin


class CastleJournal(TimestampMixin, AuditMixin, Base):
    """User journal and visited state for a castle."""

    __tablename__ = "castle_journals"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "castle_id",
            "travel_date",
            name="uq_castle_journals_user_castle_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    castle_id: Mapped[int] = mapped_column(
        ForeignKey("castles.id"),
        nullable=False,
        index=True,
    )
    visited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    travel_date: Mapped[date] = mapped_column(Date, nullable=False)
    journal_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_urls_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    style: Mapped[str] = mapped_column(String(32), nullable=False, default="notebook")

    user = relationship("User")
    castle = relationship("Castle")
    recommendations = relationship(
        "JournalRecommendation",
        back_populates="journal",
        cascade="all, delete-orphan",
        order_by="JournalRecommendation.sort_order",
    )
