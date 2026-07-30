import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

DEMO_USER_COUNT = 20
DEFAULT_DEMO_JOURNAL_COUNT = 100
RANDOM_SEED = 20260729

USER_NAMES = [
    "晨光旅人",
    "城跡手帳社",
    "小町散策",
    "石垣控",
    "御朱印路人",
    "青空遠足",
    "山城慢走",
    "海風筆記",
    "城下町咖啡",
    "旅圖收藏家",
    "櫻雨散步",
    "北國巡禮",
    "西國小旅行",
    "天守觀察員",
    "月台旅記",
    "古道午後",
    "週末百名城",
    "朱印小隊",
    "坡道與石牆",
    "町屋明信片",
]

JOURNAL_SENTENCES = [
    "抵達時天氣很好，城牆的線條比照片裡更有層次。",
    "沿著護城河慢慢走了一圈，最喜歡轉角突然出現天守的瞬間。",
    "車站到城跡的路很好逛，途中買了熱茶，剛好配著風景休息。",
    "石垣保存得很漂亮，摸起來有一種時間沉下來的安靜感。",
    "展望台看出去能把城下町收進眼裡，值得多留半小時。",
    "今天人潮不多，可以很慢地拍照，也能好好讀完解說牌。",
    "蓋章點比想像中好找，工作人員也很親切。",
    "午後光線照在屋瓦上很漂亮，這一站放進手帳剛剛好。",
    "雖然只剩遺構，但走在曲輪之間仍然能感覺當年的規模。",
    "附近小店的點心意外好吃，成為這趟小旅行的可愛註腳。",
]


def main() -> None:
    """Seed demo users and castle journals for local map activity."""
    from sqlalchemy import delete

    from app.core.database import SessionLocal, create_database_tables
    from app.models.castle import Castle
    from app.models.castle_journal import CastleJournal

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_DEMO_JOURNAL_COUNT,
        help="Total demo journal records to keep after seeding.",
    )
    args = argument_parser.parse_args()

    random_generator = random.Random(RANDOM_SEED)
    create_database_tables()
    db_session = SessionLocal()
    try:
        castles = list(db_session.query(Castle).order_by(Castle.id.asc()).all())
        if not castles:
            raise RuntimeError("No castles found. Import ToCoo castles first.")

        users = [
            _upsert_demo_user(db_session, index)
            for index in range(DEMO_USER_COUNT)
        ]
        demo_user_ids = [user.id for user in users]
        db_session.execute(
            delete(CastleJournal).where(CastleJournal.user_id.in_(demo_user_ids)),
        )
        db_session.flush()
        existing_pairs = {
            (journal.user_id, journal.castle_id, journal.travel_date)
            for journal in db_session.query(CastleJournal).all()
        }

        created_count = 0
        attempts = 0
        max_possible_count = len(users) * len(castles)
        target_count = min(args.count, max_possible_count)
        while created_count < target_count and attempts < max_possible_count * 4:
            attempts += 1
            user = random_generator.choice(users)
            castle = random_generator.choice(castles)
            travel_date = date.today() - timedelta(
                days=random_generator.randint(1, 720),
            )
            pair = (user.id, castle.id, travel_date)
            if pair in existing_pairs:
                continue

            journal = CastleJournal(
                user_id=user.id,
                castle_id=castle.id,
                visited=True,
                travel_date=travel_date,
                journal_text=_build_journal_text(random_generator, castle.name),
            )
            db_session.add(journal)
            existing_pairs.add(pair)
            created_count += 1

        db_session.commit()
        print(f"Seeded {created_count} demo journal records.")
    finally:
        db_session.close()


def _upsert_demo_user(db_session: Any, index: int) -> Any:
    from app.models.user import User

    google_sub = f"demo-user-{index + 1:02d}"
    user = db_session.query(User).filter(User.google_sub == google_sub).first()
    if user is not None:
        return user

    user = User(
        google_sub=google_sub,
        email=f"demo-user-{index + 1:02d}@example.com",
        display_name=USER_NAMES[index],
        avatar_url=None,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _build_journal_text(random_generator: random.Random, castle_name: str) -> str:
    first_sentence, second_sentence = random_generator.sample(JOURNAL_SENTENCES, 2)
    return f"{castle_name}：{first_sentence}{second_sentence}"


if __name__ == "__main__":
    main()
