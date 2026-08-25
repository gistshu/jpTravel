from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.user import User
from app.repositories.castle_repository import CastleRepository
from app.repositories.journal_repository import JournalRepository
from app.schemas.journal import (
    AccountJournalRead,
    AccountRankingRead,
    CastleJournalCollectionRead,
    JournalActivityRead,
    JournalRead,
    JournalRecommendationRead,
    JournalRecordRead,
    JournalStatsRead,
)
from app.services.castle_service import _build_official_url, _build_wikipedia_url
from app.services.journal_image_service import dump_image_urls, parse_image_urls

SAMURAI_TITLES = [
    "浪人",
    "鄉士",
    "足輕",
    "侍",
    "足輕頭",
    "侍大將",
    "家老",
    "宿老",
    "小大名",
    "大大名",
    "霸主",
    "天下人",
]
MAX_CASTLE_COUNT_FOR_TOP_TITLE = 100


class JournalService:
    """Service for user castle journal workflows."""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.castle_repository = CastleRepository(db_session)
        self.journal_repository = JournalRepository(db_session)

    def list_my_journals(self, user: User) -> list[JournalRead]:
        """Return all journal states for the current user."""
        journals = self.journal_repository.list_by_user(user.id)
        return [
            JournalRead(
                castle_id=journal.castle_id,
                visited=journal.visited,
                travel_date=journal.travel_date,
                journal_text=journal.journal_text,
                image_urls=parse_image_urls(journal.image_urls_json),
                recommendations=_build_recommendation_reads(journal.recommendations),
            )
            for journal in journals
        ]

    def update_my_journal(
        self,
        user: User,
        castle_id: int,
        visited: bool,
        travel_date: date,
        journal_text: str,
        image_urls: list[str],
        recommendations: list[dict[str, object]],
    ) -> JournalRead:
        """Update the current user's journal for one castle."""
        castle = self.castle_repository.get_by_id(castle_id)
        if castle is None:
            raise ResourceNotFoundError("城堡不存在")

        journal = self.journal_repository.upsert(
            user_id=user.id,
            castle_id=castle_id,
            visited=visited,
            travel_date=travel_date,
            journal_text=journal_text.strip(),
            image_urls_json=dump_image_urls(image_urls),
        )
        self.journal_repository.replace_recommendations(journal, recommendations)
        self.db_session.commit()
        return JournalRead(
            castle_id=journal.castle_id,
            visited=journal.visited,
            travel_date=journal.travel_date,
            journal_text=journal.journal_text,
            image_urls=parse_image_urls(journal.image_urls_json),
            recommendations=_build_recommendation_reads(journal.recommendations),
        )

    def list_latest_updates(self, limit: int) -> list[JournalActivityRead]:
        """Return latest journal updates for the public activity panel."""
        updates = self.journal_repository.list_latest_updates(limit)
        return [
            JournalActivityRead(
                castle_id=castle.id,
                user_display_name=user.display_name,
                castle_name=castle.name,
                travel_date=journal.travel_date,
                journal_text=journal.journal_text,
                image_urls=parse_image_urls(journal.image_urls_json),
                updated_at=journal.updated_at.isoformat(),
                recommendations=_build_recommendation_reads(journal.recommendations),
            )
            for journal, user, castle in updates
        ]

    def list_latest_by_castle(
        self,
        castle_id: int,
        limit: int,
    ) -> list[JournalRecordRead]:
        """Return latest public journal records for one castle."""
        castle = self.castle_repository.get_by_id(castle_id)
        if castle is None:
            raise ResourceNotFoundError("城堡不存在")

        records = self.journal_repository.list_latest_by_castle(castle_id, limit)
        visited_counts = self.journal_repository.get_visited_castle_counts_by_user_ids(
            {user.id for _, user in records},
        )
        return [
            JournalRecordRead(
                user_display_name=user.display_name,
                travel_date=journal.travel_date,
                journal_text=journal.journal_text,
                image_urls=parse_image_urls(journal.image_urls_json),
                updated_at=journal.updated_at.isoformat(),
                title=_get_samurai_title(visited_counts.get(user.id, 0)),
                title_level=_get_samurai_title_level(visited_counts.get(user.id, 0)),
                recommendations=_build_recommendation_reads(journal.recommendations),
            )
            for journal, user in records
        ]

    def list_all_by_castle(self, castle_id: int) -> CastleJournalCollectionRead:
        """Return one castle with all public journal records."""
        castle = self.castle_repository.get_by_id(castle_id)
        if castle is None:
            raise ResourceNotFoundError("城堡不存在")

        records = self.journal_repository.list_all_by_castle(castle_id)
        visited_counts = self.journal_repository.get_visited_castle_counts_by_user_ids(
            {user.id for _, user in records},
        )
        return CastleJournalCollectionRead(
            castle_id=castle.id,
            castle_name=castle.name,
            prefecture=castle.prefecture or "",
            address=castle.address,
            image_url=castle.image_url,
            wikipedia_url=_build_wikipedia_url(castle.name),
            official_url=_build_official_url(castle.source_url),
            records=[
                JournalRecordRead(
                    user_display_name=user.display_name,
                    travel_date=journal.travel_date,
                    journal_text=journal.journal_text,
                    image_urls=parse_image_urls(journal.image_urls_json),
                    updated_at=journal.updated_at.isoformat(),
                    title=_get_samurai_title(visited_counts.get(user.id, 0)),
                    title_level=_get_samurai_title_level(
                        visited_counts.get(user.id, 0),
                    ),
                    recommendations=_build_recommendation_reads(
                        journal.recommendations,
                    ),
                )
                for journal, user in records
            ],
        )

    def list_account_rankings(self, limit: int) -> list[AccountRankingRead]:
        """Return users ranked by distinct visited castle count."""
        ranked_users = self.journal_repository.list_account_rankings(limit)
        return [
            AccountRankingRead(
                rank=index + 1,
                user_id=user.id,
                user_display_name=user.display_name,
                visited_castle_count=visited_castle_count,
                title=_get_samurai_title(visited_castle_count),
                title_level=_get_samurai_title_level(visited_castle_count),
            )
            for index, (user, visited_castle_count) in enumerate(ranked_users)
        ]

    def get_public_stats(self) -> JournalStatsRead:
        """Return public aggregate journal statistics."""
        user_count, journal_count = self.journal_repository.get_public_stats()
        return JournalStatsRead(
            journal_user_count=user_count,
            journal_count=journal_count,
        )

    def list_public_by_user(self, user_id: int) -> list[AccountJournalRead]:
        """Return public visited journal records for one user."""
        from app.repositories.user_repository import UserRepository

        user = UserRepository(self.db_session).get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundError("帳號不存在")

        records = self.journal_repository.list_public_by_user(user_id)
        return [
            AccountJournalRead(
                castle_id=journal.castle_id,
                castle_name=journal.castle.name,
                user_display_name=user.display_name,
                travel_date=journal.travel_date,
                journal_text=journal.journal_text,
                image_urls=parse_image_urls(journal.image_urls_json),
                updated_at=journal.updated_at.isoformat(),
                recommendations=_build_recommendation_reads(journal.recommendations),
            )
            for journal in records
        ]


def _get_samurai_title(visited_castle_count: int) -> str:
    return SAMURAI_TITLES[_get_samurai_title_level(visited_castle_count)]


def _build_recommendation_reads(recommendations) -> list[JournalRecommendationRead]:
    return [
        JournalRecommendationRead(
            name=recommendation.name,
            category=recommendation.category,
            description=recommendation.description,
            google_maps_url=recommendation.google_maps_url,
            image_urls=parse_image_urls(recommendation.image_urls_json),
            address=recommendation.address,
            latitude=recommendation.latitude,
            longitude=recommendation.longitude,
            osm_type=recommendation.osm_type,
            osm_id=recommendation.osm_id,
            osm_url=recommendation.osm_url,
            rating=recommendation.rating,
        )
        for recommendation in recommendations
    ]


def _get_samurai_title_level(visited_castle_count: int) -> int:
    if visited_castle_count >= MAX_CASTLE_COUNT_FOR_TOP_TITLE:
        return len(SAMURAI_TITLES) - 1

    castles_per_level = MAX_CASTLE_COUNT_FOR_TOP_TITLE / len(SAMURAI_TITLES)
    return min(
        len(SAMURAI_TITLES) - 1,
        int(max(visited_castle_count, 0) / castles_per_level),
    )
