import argparse
import json
import random
import re
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import unquote

import httpx
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError
from sqlalchemy import delete

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

DB_IMAGE_ROOT = Path("static/uploads/journals")
PEXELS_SEARCH_URL = "https://www.pexels.com/zh-tw/search/日本街景/"
FALLBACK_PEXELS_IMAGE_URLS = [
    "https://images.pexels.com/photos/28535925/pexels-photo-28535925.jpeg?auto=compress&cs=tinysrgb&w=1400",
    "https://images.pexels.com/photos/18234070/pexels-photo-18234070.jpeg?auto=compress&cs=tinysrgb&w=1400",
    "https://images.pexels.com/photos/30310124/pexels-photo-30310124.jpeg?auto=compress&cs=tinysrgb&w=1400",
    "https://images.pexels.com/photos/27109414/pexels-photo-27109414.jpeg?auto=compress&cs=tinysrgb&w=1400",
    "https://images.pexels.com/photos/31053009/pexels-photo-31053009.png?auto=compress&cs=tinysrgb&w=1400",
    "https://images.pexels.com/photos/29241372/pexels-photo-29241372.jpeg?auto=compress&cs=tinysrgb&w=1400",
]
RANDOM_SEED = 20260804
DEMO_USER_COUNT = 40
DEFAULT_JOURNAL_COUNT = 2000
PEXELS_IMAGE_POOL_SIZE = 48
MAX_STORED_IMAGE_BYTES = 1024 * 1024

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
    "市電漫遊",
    "雨巷散步",
    "天守遠足",
    "街角食堂",
    "石階筆記",
    "旅印收藏",
    "城旅手札",
    "北風散策",
    "海港午後",
    "山麓小旅",
    "町並觀察",
    "古城影像",
    "旅路慢記",
    "城下町休日",
    "路地咖啡",
    "御城巡禮",
    "小巷旅人",
    "午後朱印",
    "城跡散策部",
    "旅程收集家",
]

JOURNAL_SENTENCES = [
    "沿著城下町慢慢走，路邊小店和石牆的距離比想像中更近。",
    "這趟天氣很好，拍下來的街景有一種清爽的旅行感。",
    "從車站一路走到城跡，途中剛好遇到幾間很有味道的店。",
    "城郭本身很值得看，周邊散步路線也很適合排半天。",
    "午後光線落在屋瓦和街道上，整段旅程都很舒服。",
    "這次沒有趕行程，反而發現不少適合停下來的小地方。",
    "蓋章後又在附近繞了一圈，意外收穫比預期多。",
    "街道乾淨安靜，適合一邊拍照一邊寫進手帳。",
    "從天守附近往外走，商店街和住宅區的節奏很有層次。",
    "這座城很適合搭配周邊景點一起玩，不會只是單點造訪。",
]

RECOMMENDATION_NAMES = [
    ("attraction", "城下町散步路線"),
    ("attraction", "展望台周邊"),
    ("attraction", "歷史資料館"),
    ("food", "在地定食小店"),
    ("food", "拉麵老店"),
    ("food", "咖哩食堂"),
    ("cafe", "町屋咖啡"),
    ("cafe", "車站前喫茶"),
    ("shop", "伴手禮商店"),
    ("shop", "商店街小舖"),
]

RECOMMENDATION_REASONS = [
    "參觀後順路過來很方便，適合休息一下再出發。",
    "店內氣氛很好，適合把當天的手帳內容慢慢寫完。",
    "離城堡不遠，步行就能抵達，是很自然的順遊點。",
    "價格和份量都不錯，旅途中補充體力很剛好。",
    "拍照效果很好，能補上城堡以外的街景記憶。",
    "服務親切，第一次來也不會有壓力。",
    "交通位置方便，適合安排在行程前後。",
    "這裡保留了城下町的生活感，和城堡一起看很有意思。",
]


def main() -> None:
    """Seed a large demo dataset with recommendations."""
    from app.core.database import SessionLocal, create_database_tables
    from app.models.castle import Castle
    from app.models.castle_journal import CastleJournal
    from app.models.journal_recommendation import JournalRecommendation
    from app.models.user import User

    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=DEFAULT_JOURNAL_COUNT)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--image-pool-size", type=int, default=PEXELS_IMAGE_POOL_SIZE)
    parser.add_argument(
        "--append",
        action="store_true",
        help="Keep existing journals and add new random demo records.",
    )
    args = parser.parse_args()

    random_generator = random.Random(args.seed)
    create_database_tables()
    image_pool = _ensure_pexels_image_pool(args.image_pool_size, random_generator)

    db_session = SessionLocal()
    try:
        castles = list(db_session.query(Castle).order_by(Castle.id.asc()).all())
        if not castles:
            raise RuntimeError("No castles found. Import castle data first.")

        if not args.append:
            db_session.execute(delete(JournalRecommendation))
            db_session.execute(delete(CastleJournal))
        users = [
            _upsert_demo_user(db_session, User, index)
            for index in range(DEMO_USER_COUNT)
        ]
        db_session.flush()

        created_journal_count = 0
        created_recommendation_count = 0
        used_keys: set[tuple[int, int, date]] = set(
            db_session.query(
                CastleJournal.user_id,
                CastleJournal.castle_id,
                CastleJournal.travel_date,
            ).all(),
        )
        attempts = 0
        while created_journal_count < args.count and attempts < args.count * 12:
            attempts += 1
            user = random_generator.choice(users)
            castle = random_generator.choice(castles)
            travel_date = date.today() - timedelta(
                days=random_generator.randint(1, 1200),
            )
            key = (user.id, castle.id, travel_date)
            if key in used_keys:
                continue

            journal = CastleJournal(
                user_id=user.id,
                castle_id=castle.id,
                visited=True,
                travel_date=travel_date,
                journal_text=_build_journal_text(random_generator, castle.name),
                image_urls_json=json.dumps(
                    random_generator.sample(image_pool, 2),
                    ensure_ascii=False,
                ),
            )
            db_session.add(journal)
            db_session.flush()
            used_keys.add(key)
            created_journal_count += 1

            for sort_order in range(2):
                category, name = random_generator.choice(RECOMMENDATION_NAMES)
                latitude, longitude = _jitter_coordinate(
                    random_generator,
                    castle.latitude,
                    castle.longitude,
                )
                db_session.add(
                    JournalRecommendation(
                        journal_id=journal.id,
                        user_id=user.id,
                        castle_id=castle.id,
                        name=name,
                        category=category,
                        description=random_generator.choice(RECOMMENDATION_REASONS),
                        image_urls_json=json.dumps(
                            [random_generator.choice(image_pool)],
                            ensure_ascii=False,
                        ),
                        latitude=latitude,
                        longitude=longitude,
                        osm_url=(
                            "https://www.openstreetmap.org/"
                            f"?mlat={latitude}&mlon={longitude}"
                            f"#map=18/{latitude}/{longitude}"
                        ),
                        rating=random_generator.randint(3, 5),
                        sort_order=sort_order,
                    ),
                )
                created_recommendation_count += 1

        db_session.commit()
        print(
            f"Seeded {created_journal_count} journals and "
            f"{created_recommendation_count} recommendations "
            f"with {len(image_pool)} Pexels demo images.",
        )
    finally:
        db_session.close()


def _upsert_demo_user(db_session, user_model, index: int):
    google_sub = f"demo-user-{index + 1:02d}"
    user = (
        db_session.query(user_model)
        .filter(user_model.google_sub == google_sub)
        .first()
    )
    if user is not None:
        user.display_name = USER_NAMES[index]
        return user

    user = user_model(
        google_sub=google_sub,
        email=f"demo-user-{index + 1:02d}@example.com",
        display_name=USER_NAMES[index],
        avatar_url=None,
    )
    db_session.add(user)
    return user


def _ensure_pexels_image_pool(
    image_pool_size: int,
    random_generator: random.Random,
) -> list[str]:
    DB_IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    existing_images = sorted(
        f"/static/uploads/journals/{path.name}"
        for path in DB_IMAGE_ROOT.glob("pexels_seed_*.jpg")
    )
    if len(existing_images) >= image_pool_size:
        return existing_images[:image_pool_size]

    try:
        image_urls = _extract_pexels_image_urls()
    except httpx.HTTPError:
        image_urls = FALLBACK_PEXELS_IMAGE_URLS
    random_generator.shuffle(image_urls)
    for image_url in image_urls:
        if len(existing_images) >= image_pool_size:
            break
        saved_url = _download_and_store_image(image_url)
        if saved_url:
            existing_images.append(saved_url)

    while len(existing_images) < 2:
        existing_images.append(
            _create_fallback_image(random_generator, len(existing_images)),
        )

    if existing_images:
        return existing_images

    return [_create_fallback_image(random_generator, index) for index in range(12)]


def _extract_pexels_image_urls() -> list[str]:
    response = httpx.get(
        PEXELS_SEARCH_URL,
        follow_redirects=True,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0 JPTravelSeed/0.1",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.7",
        },
    )
    response.raise_for_status()
    urls = set()
    pattern = r"https://images\.pexels\.com/photos/[^\"'\\<>\s]+"
    for raw_url in re.findall(pattern, response.text):
        url = unquote(raw_url).replace("\\u0026", "&")
        url = url.split("?")[0]
        urls.add(f"{url}?auto=compress&cs=tinysrgb&w=1400")
    return sorted(urls)


def _download_and_store_image(image_url: str) -> str | None:
    try:
        response = httpx.get(image_url, timeout=30, follow_redirects=True)
        response.raise_for_status()
        from io import BytesIO

        with Image.open(BytesIO(response.content)) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode not in {"RGB", "L"}:
                image = image.convert("RGB")
            filename = f"pexels_seed_{uuid.uuid4().hex}.jpg"
            output_path = DB_IMAGE_ROOT / filename
            _save_under_size_limit(image, output_path)
            return f"/static/uploads/journals/{filename}"
    except (httpx.HTTPError, OSError, UnidentifiedImageError):
        return None


def _create_fallback_image(random_generator: random.Random, index: int) -> str:
    image = Image.new(
        "RGB",
        (1200, 900),
        random_generator.choice(["#e9f1fb", "#fff2cd", "#eef3f1"]),
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle((90, 90, 1110, 810), outline="#b72f35", width=10)
    draw.text((140, 140), f"Japan street demo {index + 1}", fill="#182026")
    filename = f"pexels_seed_fallback_{uuid.uuid4().hex}.jpg"
    output_path = DB_IMAGE_ROOT / filename
    _save_under_size_limit(image, output_path)
    return f"/static/uploads/journals/{filename}"


def _save_under_size_limit(image: Image.Image, output_path: Path) -> None:
    working_image = image.copy()
    for max_side in (1600, 1400, 1200, 1000, 800):
        working_image.thumbnail((max_side, max_side))
        for quality in (84, 78, 72, 66, 60):
            working_image.save(
                output_path,
                format="JPEG",
                quality=quality,
                optimize=True,
            )
            if output_path.stat().st_size <= MAX_STORED_IMAGE_BYTES:
                return
    raise RuntimeError("Image exceeded 1MB after compression.")


def _build_journal_text(random_generator: random.Random, castle_name: str) -> str:
    sentences = random_generator.sample(JOURNAL_SENTENCES, 2)
    return f"{castle_name}：{''.join(sentences)}"


def _jitter_coordinate(
    random_generator: random.Random,
    latitude: float,
    longitude: float,
) -> tuple[float, float]:
    return (
        round(latitude + random_generator.uniform(-0.012, 0.012), 7),
        round(longitude + random_generator.uniform(-0.012, 0.012), 7),
    )


if __name__ == "__main__":
    main()
