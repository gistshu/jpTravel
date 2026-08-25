from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, TimestampMixin


class JournalRecommendation(TimestampMixin, AuditMixin, Base):
    """Place recommended by a user for one castle journal."""

    __tablename__ = "journal_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journal_id: Mapped[int] = mapped_column(
        ForeignKey("castle_journals.id"),
        nullable=False,
        index=True,
    )
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
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    google_maps_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_urls_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    osm_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    osm_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    osm_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    journal = relationship("CastleJournal", back_populates="recommendations")
    user = relationship("User")
    castle = relationship("Castle")
