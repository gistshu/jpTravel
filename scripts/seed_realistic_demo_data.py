"""Seed realistic demo journals using real castle photos and nearby places.

Stage 1 (fetch, resumable): for every official castle, collect
- castle photos from Wikimedia Commons (geosearch around the castle),
- nearby attractions / restaurants / cafes / shops from OpenStreetMap (Overpass),
- photos of nearby attractions from Wikimedia Commons.
Photos are downloaded, compressed and cached under DEMO_IMAGE_ROOT, together with
a JSON cache and a credits file (Commons photos are CC licensed and need attribution).

Stage 2 (seed): delete journals of demo users and generate travel trips for
DEMO_USER_COUNT demo users, with season-aware journal text and recommendations
that point to real nearby places.
"""

import argparse
import json
import logging
import math
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime, timedelta
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

logger = logging.getLogger("seed_realistic_demo_data")

DEMO_IMAGE_ROOT = PROJECT_ROOT / "static/uploads/journals/demo_real"
DEMO_IMAGE_URL_PREFIX = "/static/uploads/journals/demo_real"
CACHE_PATH = DEMO_IMAGE_ROOT / "places_cache.json"
CREDITS_PATH = DEMO_IMAGE_ROOT / "CREDITS.json"

USER_AGENT = "JPTravelDemoSeed/0.2 (non-commercial demo data; contact: site maintainer)"
COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
OVERPASS_LOCKS = {url: threading.Lock() for url in OVERPASS_URLS}
WIKIMEDIA_LOCK = threading.Lock()
WIKIMEDIA_MIN_INTERVAL_SECONDS = 1.0
_last_wikimedia_request_at = 0.0

RANDOM_SEED = 20261005
DEMO_USER_COUNT = 50
DEFAULT_JOURNAL_COUNT = 3000
CASTLE_IMAGE_LIMIT = 5
FETCH_WORKERS = 4
MAX_JOURNALS_PER_USER = 210
ATTRACTION_IMAGE_POI_LIMIT = 4
MAX_STORED_IMAGE_BYTES = 1024 * 1024
STORED_IMAGE_MAX_SIDE = 1024
FIRST_TRAVEL_DATE = date(2022, 1, 1)
LAST_TRAVEL_DATE = date(2026, 9, 28)

EXCLUDED_IMAGE_TITLE_PATTERN = re.compile(
    r"map|plan|diagram|logo|stamp|sign|board|pamphlet|ticket|panel|"
    r"地図|案内|看板|縄張|説明|図|svg|png",
    re.IGNORECASE,
)
CASTLE_IMAGE_TITLE_PATTERN = re.compile(
    r"castle|城|jo[ _-]|jō|ruins|tenshu|yagura", re.IGNORECASE
)

EXISTING_TENSHU_CASTLES = {
    "弘前城",
    "松本城",
    "丸岡城",
    "犬山城",
    "彦根城",
    "姫路城",
    "松江城",
    "備中松山城",
    "丸亀城",
    "松山城",
    "宇和島城",
    "高知城",
}
RECONSTRUCTED_TENSHU_CASTLES = {
    "松前城",
    "会津若松城",
    "白河小峰城",
    "小田原城",
    "岐阜城",
    "掛川城",
    "名古屋城",
    "岡崎城",
    "伊賀上野城",
    "大阪城",
    "和歌山城",
    "岡山城",
    "福山城",
    "広島城",
    "岩国城",
    "今治城",
    "大洲城",
    "島原城",
    "熊本城",
    "平戸城",
    "首里城",
    "郡上八幡城",
    "大垣城",
    "浜松城",
    "福知山城",
    "岸和田城",
    "洲本城",
    "小倉城",
    "唐津城",
    "中津城",
    "高田城",
    "富山城",
    "越前大野城",
    "墨俣城",
    "上山城",
    "白石城",
    "忍城",
    "大多喜城",
}
FAMOUS_CASTLES = {
    "姫路城",
    "大阪城",
    "熊本城",
    "松本城",
    "名古屋城",
    "二条城",
    "彦根城",
    "犬山城",
    "松江城",
    "竹田城",
    "首里城",
    "五稜郭",
    "弘前城",
    "江戸城",
    "金沢城",
    "小田原城",
    "会津若松城",
    "松山城",
    "高知城",
    "備中松山城",
    "岡山城",
    "広島城",
    "丸亀城",
    "宇和島城",
    "安土城",
    "郡上八幡城",
}

USER_NAMES = [
    "城跡散步人",
    "Kenji_T",
    "百名城制霸中",
    "小米的城旅",
    "石垣控阿哲",
    "御城印收集家",
    "Alice Lin",
    "天守閣觀察員",
    "週末去日本",
    "山城攻略組",
    "旅行的貓",
    "Mika醬",
    "鐵道與城",
    "櫻花季必去",
    "北海道到沖繩",
    "阿翔的日本筆記",
    "城下町咖啡",
    "自駕日本中",
    "Joe Chen",
    "紅葉狩人",
    "一人旅小雨",
    "大叔愛日本",
    "小林的旅程",
    "背包客Wei",
    "雨天也要攻城",
    "戰國迷阿凱",
    "日本百名城の旅",
    "Yuki旅日記",
    "慢遊關西",
    "東北秘境派",
    "九州吃吃喝喝",
    "四國遍路中",
    "Ryan & Amy",
    "城郭建築迷",
    "信長粉",
    "親子日本遊",
    "退休後去看城",
    "攝影師阿德",
    "Hana散策",
    "城堡收集冊",
    "名城印章本",
    "古地圖愛好者",
    "夏天去看城",
    "小鎮與城",
    "Sakura_Lee",
    "山陰山陽慢旅",
    "北陸新幹線",
    "東海道漫步",
    "日本自由行老手",
    "城跡巡禮",
]

SEASON_LINES = {
    1: ["一月的空氣很冷冽，石垣上還留著薄霜。", "新年剛過，城內遊客很少，可以慢慢走。"],
    2: ["二月來訪，城內的梅花剛開始綻放。", "天氣很冷但非常晴朗，城在藍天下特別清楚。"],
    3: [
        "三月底櫻花開了五六分，已經有不少人在城內賞花。",
        "春天剛到，風還有點涼，但陽光很舒服。",
    ],
    4: [
        "剛好遇上櫻花滿開，石垣配櫻花真的太美了。",
        "四月初人潮不少，但櫻花完全值得。",
        "櫻吹雪的時候走在城內，像在看電影。",
    ],
    5: ["五月新綠很舒服，整片樹林都是嫩綠色。", "黃金週人有點多，建議一早就到。"],
    6: ["梅雨季節來訪，雨中的城另有一番味道。", "六月的紫陽花開得很好，人也不多。"],
    7: ["七月非常熱，記得多帶水。", "夏天的藍天和城郭很搭，拍起來很有精神。"],
    8: ["八月酷暑，爬坡時汗流浹背，但風景值得。", "盂蘭盆節期間，城下町比平常熱鬧。"],
    9: ["九月還有點熱，不過傍晚的風很舒服。", "颱風剛過，天空特別乾淨。"],
    10: ["十月秋高氣爽，非常適合走城跡。", "秋天的光線很柔和，拍照特別好看。"],
    11: ["十一月紅葉正紅，楓葉配上石垣超美。", "晚秋來訪，銀杏和楓葉都變色了。"],
    12: ["十二月很冷，但遊客少，可以安靜地逛。", "下了點小雪，城看起來像明信片一樣。"],
}
EXISTING_TENSHU_LINES = [
    "現存天守果然有氛圍，木造樓梯非常陡，要抓著扶手慢慢爬。",
    "能走進江戶時代留下來的天守，感覺很不一樣，木頭的味道很特別。",
    "天守不大，但每一層的梁柱都很有看頭。",
]
RECONSTRUCTED_TENSHU_LINES = [
    "天守內部是資料館，展示很豐富，可以了解城的歷史。",
    "從天守最上層眺望整個城下町，視野很好。",
    "天守是重建的，但外觀很有氣勢，石垣則是當年留下來的。",
]
RUINS_LINES = [
    "主要是城跡，石垣和堀切保存得很好。",
    "沿著登城道往上走大約二三十分鐘，到本丸時視野一下子打開。",
    "雖然沒有天守，但土壘和曲輪的配置很好懂，看說明牌就能想像當年的樣子。",
    "城跡很安靜，幾乎只有我們，很適合慢慢看遺構。",
    "高石垣非常壯觀，站在下面看很有壓迫感。",
]
ACCESS_LINES = [
    "從車站步行大約{minutes}分鐘就到了。",
    "這次租車自駕，停車場就在城旁邊，很方便。",
    "搭市區巴士過去，班次不算多，最好先查好時間。",
    "騎共享單車過去，沿途風景很好。",
    "從車站搭計程車大約十分鐘，回程用走的順便逛城下町。",
]
STAMP_LINES = [
    "百名城印章在{place}蓋到了。",
    "印章放在{place}，記得在開放時間內去。",
    "順利蓋到印章，也買了御城印當紀念。",
]
CONTINUED_STAMP_LINES = [
    "續百名城印章在{place}蓋到了。",
    "續百名城的印章放在{place}，差點錯過。",
]
STAMP_PLACES = ["管理事務所", "天守入口", "資料館售票處", "觀光案內所", "附近的歷史館"]
DURATION_LINES = [
    "整個逛下來大約兩個小時。",
    "停留一個半小時左右，時間剛好。",
    "花了半天慢慢逛，完全不覺得累。",
    "時間有點趕，只逛了一小時，下次想再慢慢看。",
]
CLOSING_LINES = [
    "下次想在不同季節再來一次。",
    "推薦給喜歡城的朋友。",
    "是這趟旅程中最喜歡的一座城。",
    "比想像中更好逛，很值得。",
    "又往制霸前進了一步！",
    "",
]
SHORT_JOURNALS = [
    "天氣很好，終於蓋到印章了！",
    "時間不多，快速逛一圈，下次再來。",
    "雨很大，只拍了幾張照片就撤退了。",
    "人好多，但城真的很漂亮。",
]

RECOMMENDATION_LINES = {
    "attraction": [
        "從城走過去大約{minutes}分鐘，{kind}本身也很值得看。",
        "跟城堡一起逛剛好，可以補充這一帶的歷史背景。",
        "人不多，可以安靜地看，很推薦。",
        "可以從另一個角度看這一帶的風景，拍照很好看。",
    ],
    "food": [
        "中午在這裡吃{kind}，份量足、價格實在。",
        "在地人很多的店，{kind}很好吃。",
        "排了二十分鐘左右，但很值得。",
        "店主很親切，用簡單的日文和手勢也能點餐。",
    ],
    "cafe": [
        "逛完城來這裡休息，咖啡和甜點都很好。",
        "店內安靜，適合整理照片和寫筆記。",
        "離城不遠，走累了剛好進來坐一下。",
    ],
    "shop": [
        "買了在地點心當伴手禮，家人都很喜歡。",
        "和菓子很精緻，適合送人。",
        "店員很親切，還讓我們試吃。",
    ],
}
CUISINE_LABELS = {
    "ramen": "拉麵",
    "sushi": "壽司",
    "soba": "蕎麥麵",
    "udon": "烏龍麵",
    "japanese": "和食",
    "regional": "鄉土料理",
    "noodle": "麵食",
    "curry": "咖哩",
    "yakitori": "烤雞串",
    "okonomiyaki": "大阪燒",
    "tempura": "天婦羅",
    "unagi": "鰻魚飯",
    "chinese": "中華料理",
    "italian": "義大利料理",
    "burger": "漢堡",
    "tonkatsu": "炸豬排",
    "donburi": "丼飯",
    "seafood": "海鮮",
    "steak_house": "牛排",
    "pizza": "披薩",
    "french": "法式料理",
    "yakiniku": "燒肉",
    "gyoza": "餃子",
    "kaiseki": "會席料理",
}
ATTRACTION_KIND_LABELS = {
    "museum": "博物館",
    "gallery": "美術館",
    "viewpoint": "展望點",
    "attraction": "景點",
    "garden": "庭園",
    "shinto": "神社",
    "buddhist": "寺院",
    "building": "歷史建築",
    "city_gate": "城門",
    "temple": "寺院",
    "ruins": "遺跡",
}


def main() -> None:
    """Run fetch and/or seed stages."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=DEFAULT_JOURNAL_COUNT)
    parser.add_argument("--users", type=int, default=DEMO_USER_COUNT)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--fetch-only", action="store_true")
    parser.add_argument("--seed-only", action="store_true")
    args = parser.parse_args()

    from app.core.database import SessionLocal, create_database_tables
    from app.models.castle import Castle

    create_database_tables()
    db_session = SessionLocal()
    try:
        castles = list(
            db_session.scalars(
                select(Castle)
                .where(Castle.castle_series.in_(["original", "continued"]))
                .order_by(Castle.id),
            ),
        )
        if not args.seed_only:
            fetch_castle_places(castles)
        if not args.fetch_only:
            seed_journals(db_session, castles, args.count, args.users, args.seed)
    finally:
        db_session.close()


# ---------------------------------------------------------------------------
# Stage 1: fetch real photos and places
# ---------------------------------------------------------------------------


def fetch_castle_places(castles: list) -> None:
    """Fetch and cache photos and nearby places for each castle (resumable)."""
    DEMO_IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    cache = _load_json(CACHE_PATH, {})
    credits = _load_json(CREDITS_PATH, {})
    pending = [
        castle
        for castle in castles
        if not cache.get(str(castle.id), {}).get("complete")
    ]
    logger.info(
        "%d castles cached, %d to fetch", len(castles) - len(pending), len(pending)
    )
    with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as executor:
        futures = {
            executor.submit(_fetch_one_castle, castle): castle for castle in pending
        }
        for done_count, future in enumerate(as_completed(futures), start=1):
            castle = futures[future]
            try:
                entry, castle_credits = future.result()
            except (httpx.HTTPError, OSError, ValueError) as error:
                logger.warning("Skip %s: %s", castle.name, error)
                continue
            cache[str(castle.id)] = entry
            credits.update(castle_credits)
            _write_json(CACHE_PATH, cache)
            _write_json(CREDITS_PATH, credits)
            logger.info(
                "[%d/%d] %s: %d photos, %d places",
                done_count,
                len(pending),
                castle.name,
                len(entry["castle_images"]),
                len(entry["places"]),
            )


def _fetch_one_castle(castle) -> tuple[dict, dict]:
    castle_credits: dict = {}
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=60,
        follow_redirects=True,
    ) as client:
        entry = {
            "castle_images": _fetch_castle_images(client, castle, castle_credits),
            "places": _fetch_nearby_places(client, castle),
        }
        _attach_place_images(client, castle, entry, castle_credits)
    entry["complete"] = True
    return entry, castle_credits


def _fetch_castle_images(client: httpx.Client, castle, credits: dict) -> list[str]:
    candidates = []
    for radius in (500, 1500):
        candidates = _commons_geosearch(
            client, castle.latitude, castle.longitude, radius, 80
        )
        if len(candidates) >= CASTLE_IMAGE_LIMIT:
            break
    candidates.sort(
        key=lambda item: (
            not CASTLE_IMAGE_TITLE_PATTERN.search(item["title"]),
            item["distance"],
        ),
    )
    images = []
    for candidate in candidates:
        if len(images) >= CASTLE_IMAGE_LIMIT:
            break
        filename = f"castle_{castle.id}_{len(images) + 1}.jpg"
        stored_url = _download_commons_image(client, candidate, filename, credits)
        if stored_url:
            images.append(stored_url)

    if not images and castle.image_url:
        stored_url = _download_image(
            client,
            castle.image_url.replace("/250px-", "/960px-"),
            f"castle_{castle.id}_fallback.jpg",
        )
        if stored_url:
            images.append(stored_url)
    return images


def _fetch_nearby_places(client: httpx.Client, castle) -> list[dict]:
    places: list[dict] = []
    for radius in (1200, 3000):
        elements = _overpass_query(client, castle.latitude, castle.longitude, radius)
        places = _select_places(elements, castle)
        if len(places) >= 8:
            break
    return places


def _overpass_query(
    client: httpx.Client, latitude: float, longitude: float, radius: int
) -> list:
    around = f"around:{radius},{latitude},{longitude}"
    query = f"""
[out:json][timeout:90];
(
  nwr({around})["tourism"~"^(museum|gallery|viewpoint|attraction)$"]["name"];
  nwr({around})["amenity"~"^(restaurant|cafe)$"]["name"];
  nwr({around})["shop"~"^(confectionery|bakery|gift|tea)$"]["name"];
  nwr({around})["historic"~"^(building|city_gate|temple|ruins)$"]["name"];
  nwr({around})["amenity"="place_of_worship"]["name"]["wikidata"];
  nwr({around})["leisure"="garden"]["name"];
);
out center tags;
"""
    server_offset = random.randrange(len(OVERPASS_URLS))
    for attempt in range(8):
        url = OVERPASS_URLS[(attempt + server_offset) % len(OVERPASS_URLS)]
        try:
            with OVERPASS_LOCKS[url]:
                response = client.post(url, data={"data": query}, timeout=120)
                if response.status_code == 200:
                    elements = response.json().get("elements", [])
                    time.sleep(1.0)
                    return elements
            logger.warning("Overpass %s returned %s", url, response.status_code)
        except (httpx.HTTPError, ValueError) as error:
            logger.warning("Overpass %s failed: %s", url, error)
        time.sleep(5 * (attempt + 1))
    raise OSError("Overpass unavailable, castle will be retried on the next run.")


def _select_places(elements: list, castle) -> list[dict]:
    seen_names: set[str] = set()
    places = []
    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name", "").strip()
        if not name or name in seen_names or castle.name in name:
            continue
        category, kind = _classify_place(tags)
        if not category:
            continue
        latitude = element.get("lat") or element.get("center", {}).get("lat")
        longitude = element.get("lon") or element.get("center", {}).get("lon")
        if latitude is None or longitude is None:
            continue
        seen_names.add(name)
        places.append(
            {
                "name": name,
                "category": category,
                "kind": kind,
                "latitude": round(latitude, 7),
                "longitude": round(longitude, 7),
                "osm_type": element["type"],
                "osm_id": str(element["id"]),
                "address": _build_address(tags),
                "distance": round(
                    _distance_meters(
                        castle.latitude, castle.longitude, latitude, longitude
                    ),
                ),
                "images": [],
            },
        )

    places.sort(key=lambda place: place["distance"])
    limits = {"attraction": 8, "food": 10, "cafe": 5, "shop": 4}
    selected = []
    for category, limit in limits.items():
        selected.extend(
            [place for place in places if place["category"] == category][:limit]
        )
    return selected


def _classify_place(tags: dict) -> tuple[str | None, str]:
    amenity = tags.get("amenity")
    if amenity in {"restaurant", "cafe"}:
        if tags.get("brand") or tags.get("brand:wikidata"):
            return None, ""
        if amenity == "cafe":
            return "cafe", "咖啡"
        cuisine = tags.get("cuisine", "").split(";")[0]
        return "food", CUISINE_LABELS.get(cuisine, "定食")
    if tags.get("shop"):
        if tags.get("brand"):
            return None, ""
        return "shop", "伴手禮"
    if amenity == "place_of_worship":
        return "attraction", ATTRACTION_KIND_LABELS.get(
            tags.get("religion", ""), "寺社"
        )
    tourism = tags.get("tourism")
    if tourism == "attraction" and not (tags.get("wikidata") or tags.get("wikipedia")):
        return None, ""
    kind_key = tourism or tags.get("historic") or tags.get("leisure") or "attraction"
    return "attraction", ATTRACTION_KIND_LABELS.get(kind_key, "景點")


def _build_address(tags: dict) -> str | None:
    if tags.get("addr:full"):
        return tags["addr:full"]
    parts = [
        tags.get(key, "")
        for key in (
            "addr:province",
            "addr:city",
            "addr:quarter",
            "addr:neighbourhood",
            "addr:block_number",
            "addr:housenumber",
        )
    ]
    address = "".join(parts)
    return address or None


def _attach_place_images(
    client: httpx.Client,
    castle,
    entry: dict,
    credits: dict,
) -> None:
    used_titles = {
        info["title"] for url, info in credits.items() if url in entry["castle_images"]
    }
    attractions = [
        place for place in entry["places"] if place["category"] == "attraction"
    ]
    for place_index, place in enumerate(attractions[:ATTRACTION_IMAGE_POI_LIMIT]):
        candidates = _commons_geosearch(
            client, place["latitude"], place["longitude"], 100, 15
        )
        for candidate in candidates:
            if candidate["title"] in used_titles:
                continue
            filename = f"place_{castle.id}_{place_index + 1}.jpg"
            stored_url = _download_commons_image(client, candidate, filename, credits)
            if stored_url:
                used_titles.add(candidate["title"])
                place["images"].append(stored_url)
                break


def _commons_geosearch(
    client: httpx.Client,
    latitude: float,
    longitude: float,
    radius: int,
    limit: int,
) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "geosearch",
        "ggsnamespace": 6,
        "ggscoord": f"{latitude}|{longitude}",
        "ggsradius": radius,
        "ggslimit": limit,
        "prop": "imageinfo|coordinates",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 960,
        "iiextmetadatafilter": "LicenseShortName|Artist",
    }
    payload = _get_json_with_retry(client, COMMONS_API_URL, params)
    pages = payload.get("query", {}).get("pages", {})
    candidates = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        title = page.get("title", "")
        if info.get("mime") != "image/jpeg" or EXCLUDED_IMAGE_TITLE_PATTERN.search(
            title
        ):
            continue
        if info.get("width", 0) < 800 or info.get("height", 0) < 500:
            continue
        coordinates = (page.get("coordinates") or [{}])[0]
        metadata = info.get("extmetadata", {})
        candidates.append(
            {
                "title": title,
                "thumb_url": info.get("thumburl"),
                "page_url": info.get("descriptionurl"),
                "license": metadata.get("LicenseShortName", {}).get("value", ""),
                "artist": re.sub(
                    r"<[^>]+>", "", metadata.get("Artist", {}).get("value", "")
                ).strip(),
                "distance": _distance_meters(
                    latitude,
                    longitude,
                    coordinates.get("lat", latitude),
                    coordinates.get("lon", longitude),
                ),
            },
        )
    candidates.sort(key=lambda item: item["distance"])
    return candidates


def _wait_for_wikimedia_slot() -> None:
    """Keep all Wikimedia requests (API and thumbnails) at most one per interval."""
    global _last_wikimedia_request_at
    with WIKIMEDIA_LOCK:
        wait_seconds = (
            _last_wikimedia_request_at
            + WIKIMEDIA_MIN_INTERVAL_SECONDS
            - time.monotonic()
        )
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        _last_wikimedia_request_at = time.monotonic()


def _get_json_with_retry(client: httpx.Client, url: str, params: dict) -> dict:
    for attempt in range(6):
        _wait_for_wikimedia_slot()
        try:
            response = client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            logger.warning("GET %s returned %s", url, response.status_code)
        except (httpx.HTTPError, ValueError) as error:
            logger.warning("GET %s failed: %s", url, error)
        time.sleep(10 * (attempt + 1))
    raise OSError("Wikimedia API unavailable, castle will be retried on the next run.")


def _download_commons_image(
    client: httpx.Client,
    candidate: dict,
    filename: str,
    credits: dict,
) -> str | None:
    if not candidate.get("thumb_url"):
        return None
    stored_url = _download_image(client, candidate["thumb_url"], filename)
    if stored_url:
        credits[stored_url] = {
            "title": candidate["title"],
            "page_url": candidate["page_url"],
            "artist": candidate["artist"],
            "license": candidate["license"],
        }
    return stored_url


def _download_image(client: httpx.Client, image_url: str, filename: str) -> str | None:
    output_path = DEMO_IMAGE_ROOT / filename
    stored_url = f"{DEMO_IMAGE_URL_PREFIX}/{filename}"
    if output_path.exists():
        return stored_url
    for attempt in range(4):
        try:
            _wait_for_wikimedia_slot()
            response = client.get(image_url)
            if response.status_code == 429:
                time.sleep(15 * (attempt + 1))
                continue
            response.raise_for_status()
            with Image.open(BytesIO(response.content)) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                _save_under_size_limit(image, output_path)
            time.sleep(0.4)
            return stored_url
        except (httpx.HTTPError, OSError, UnidentifiedImageError) as error:
            logger.warning("Download failed %s: %s", image_url, error)
            time.sleep(2)
    return None


def _save_under_size_limit(image: Image.Image, output_path: Path) -> None:
    working_image = image.copy()
    working_image.thumbnail((STORED_IMAGE_MAX_SIDE, STORED_IMAGE_MAX_SIDE))
    for quality in (82, 74, 66, 58):
        working_image.save(output_path, format="JPEG", quality=quality, optimize=True)
        if output_path.stat().st_size <= MAX_STORED_IMAGE_BYTES:
            return
    raise OSError("Image exceeded 1MB after compression.")


# ---------------------------------------------------------------------------
# Stage 2: generate journals
# ---------------------------------------------------------------------------


def seed_journals(
    db_session,
    castles: list,
    journal_count: int,
    user_count: int,
    seed: int,
) -> None:
    """Replace demo users' journals with realistic generated trips."""
    from app.models.castle_journal import CastleJournal
    from app.models.journal_recommendation import JournalRecommendation
    from app.models.user import User

    cache = _load_json(CACHE_PATH, {})
    if not cache:
        raise RuntimeError("No cached places. Run without --seed-only first.")
    random_generator = random.Random(seed)

    users = [_upsert_demo_user(db_session, User, index) for index in range(user_count)]
    db_session.flush()
    demo_user_ids = [user.id for user in users]
    all_demo_user_ids = list(
        db_session.scalars(select(User.id).where(User.google_sub.like("demo-user-%"))),
    )
    db_session.execute(
        delete(JournalRecommendation).where(
            JournalRecommendation.user_id.in_(all_demo_user_ids),
        ),
    )
    db_session.execute(
        delete(CastleJournal).where(CastleJournal.user_id.in_(all_demo_user_ids)),
    )

    castle_weights = {castle.id: _castle_weight(castle) for castle in castles}
    quotas = _user_quotas(journal_count, len(users), random_generator)
    planned = []
    for user_id, quota in zip(demo_user_ids, quotas, strict=True):
        planned.extend(
            _plan_user_trips(user_id, quota, castles, castle_weights, random_generator),
        )

    now = datetime.now(UTC)
    journal_total = 0
    recommendation_total = 0
    for plan in planned:
        castle = plan["castle"]
        entry = cache.get(str(castle.id), {})
        recommendations = _pick_recommendations(entry, random_generator)
        posted_at = _posted_at(plan["travel_date"], now, random_generator)
        journal = CastleJournal(
            user_id=plan["user_id"],
            castle_id=castle.id,
            visited=True,
            travel_date=plan["travel_date"],
            journal_text=_build_journal_text(plan, recommendations, random_generator),
            image_urls_json=json.dumps(
                _pick_journal_images(entry, random_generator),
                ensure_ascii=False,
            ),
            created_at=posted_at,
            updated_at=posted_at,
        )
        db_session.add(journal)
        db_session.flush()
        journal_total += 1

        for sort_order, place in enumerate(recommendations):
            db_session.add(
                JournalRecommendation(
                    journal_id=journal.id,
                    user_id=plan["user_id"],
                    castle_id=castle.id,
                    name=place["name"],
                    category=place["category"],
                    description=_build_recommendation_text(place, random_generator),
                    image_urls_json=json.dumps(place["images"][:1], ensure_ascii=False),
                    address=place["address"],
                    latitude=place["latitude"],
                    longitude=place["longitude"],
                    osm_type=place["osm_type"],
                    osm_id=place["osm_id"],
                    osm_url=f"https://www.openstreetmap.org/{place['osm_type']}/{place['osm_id']}",
                    rating=random_generator.choices([3, 4, 5], weights=[15, 45, 40])[0],
                    sort_order=sort_order,
                    created_at=posted_at,
                    updated_at=posted_at,
                ),
            )
            recommendation_total += 1

    db_session.commit()
    logger.info(
        "Seeded %d journals, %d recommendations for %d demo users.",
        journal_total,
        recommendation_total,
        len(users),
    )


def _upsert_demo_user(db_session, user_model, index: int):
    google_sub = f"demo-user-{index + 1:02d}"
    user = db_session.scalars(
        select(user_model).where(user_model.google_sub == google_sub),
    ).first()
    if user is None:
        user = user_model(
            google_sub=google_sub,
            email=f"{google_sub}@example.com",
            display_name=USER_NAMES[index],
            avatar_url=None,
        )
        db_session.add(user)
    user.display_name = USER_NAMES[index]
    return user


def _castle_weight(castle) -> float:
    weight = 1.6 if castle.castle_series == "original" else 1.0
    if castle.name in FAMOUS_CASTLES:
        weight *= 3.0
    return weight


def _user_quotas(
    total: int, user_count: int, random_generator: random.Random
) -> list[int]:
    raw_weights = [
        (1 / (rank + 2) ** 0.85) * random_generator.uniform(0.85, 1.15)
        for rank in range(user_count)
    ]
    weight_sum = sum(raw_weights)
    quotas = [max(3, round(total * weight / weight_sum)) for weight in raw_weights]
    for _ in range(10):
        excess = sum(max(0, quota - MAX_JOURNALS_PER_USER) for quota in quotas)
        if excess == 0:
            break
        quotas = [min(quota, MAX_JOURNALS_PER_USER) for quota in quotas]
        open_indexes = [
            index for index, quota in enumerate(quotas) if quota < MAX_JOURNALS_PER_USER
        ]
        open_weight = sum(raw_weights[index] for index in open_indexes)
        for index in open_indexes:
            quotas[index] += round(excess * raw_weights[index] / open_weight)
    quotas[-1] += total - sum(quotas)
    return quotas


def _plan_user_trips(
    user_id: int,
    quota: int,
    castles: list,
    castle_weights: dict[int, float],
    random_generator: random.Random,
) -> list[dict]:
    plans: list[dict] = []
    visited_ids: set[int] = set()
    used_keys: set[tuple[int, date]] = set()
    while len(plans) < quota:
        trip_start = _random_travel_date(random_generator)
        unvisited = [castle for castle in castles if castle.id not in visited_ids]
        pool = unvisited if unvisited and random_generator.random() > 0.05 else castles
        current = random_generator.choices(
            pool,
            weights=[castle_weights[castle.id] for castle in pool],
        )[0]
        trip_length = random_generator.choices(
            [1, 2, 3, 4, 5], weights=[25, 30, 25, 13, 7]
        )[0]
        travel_date = trip_start
        previous_castle = None
        previous_date = None
        for day_index in range(trip_length):
            if len(plans) >= quota or travel_date > LAST_TRAVEL_DATE:
                break
            key = (current.id, travel_date)
            if key not in used_keys:
                used_keys.add(key)
                visited_ids.add(current.id)
                plans.append(
                    {
                        "user_id": user_id,
                        "castle": current,
                        "travel_date": travel_date,
                        "trip_index": day_index + 1,
                        "previous_castle": previous_castle,
                        "same_day": previous_date == travel_date,
                    },
                )
            previous_castle = current
            previous_date = travel_date
            next_castle = _nearest_unvisited(
                current, castles, visited_ids, random_generator
            )
            if next_castle is None:
                break
            current = next_castle
            if random_generator.random() > 0.25:
                travel_date += timedelta(days=1)
    return plans


def _nearest_unvisited(current, castles: list, visited_ids: set[int], random_generator):
    candidates = sorted(
        (
            (
                _distance_meters(
                    current.latitude,
                    current.longitude,
                    castle.latitude,
                    castle.longitude,
                ),
                castle,
            )
            for castle in castles
            if castle.id not in visited_ids and castle.id != current.id
        ),
        key=lambda item: item[0],
    )[:4]
    candidates = [item for item in candidates if item[0] < 150_000]
    if not candidates:
        return None
    return random_generator.choice(candidates)[1]


def _random_travel_date(random_generator: random.Random) -> date:
    month_weights = [5, 5, 10, 16, 11, 5, 7, 10, 7, 11, 13, 6]
    while True:
        year = random_generator.randint(FIRST_TRAVEL_DATE.year, LAST_TRAVEL_DATE.year)
        month = random_generator.choices(range(1, 13), weights=month_weights)[0]
        day = random_generator.randint(1, 28)
        travel_date = date(year, month, day)
        if FIRST_TRAVEL_DATE <= travel_date <= LAST_TRAVEL_DATE:
            return travel_date


def _posted_at(
    travel_date: date, now: datetime, random_generator: random.Random
) -> datetime:
    posted = datetime(
        travel_date.year,
        travel_date.month,
        travel_date.day,
        tzinfo=UTC,
    ) + timedelta(
        days=random_generator.choices(
            [0, 1, 3, 7, 14, 30], weights=[30, 25, 20, 12, 8, 5]
        )[0],
        hours=random_generator.randint(10, 23),
        minutes=random_generator.randint(0, 59),
    )
    return min(posted, now - timedelta(minutes=random_generator.randint(5, 600)))


def _pick_journal_images(entry: dict, random_generator: random.Random) -> list[str]:
    images = entry.get("castle_images", [])
    if not images:
        return []
    image_count = random_generator.choices(
        [0, 1, 2, 3, 4, 5], weights=[22, 20, 25, 18, 10, 5]
    )[0]
    return random_generator.sample(images, min(image_count, len(images)))


def _pick_recommendations(entry: dict, random_generator: random.Random) -> list[dict]:
    places = entry.get("places", [])
    if not places or random_generator.random() > 0.35:
        return []
    count = random_generator.choices([1, 2, 3], weights=[70, 25, 5])[0]
    weights = [
        {"attraction": 45, "food": 35, "cafe": 15, "shop": 5}[place["category"]]
        * (2.0 if place["images"] else 1.0)
        for place in places
    ]
    picked: list[dict] = []
    for _ in range(count * 3):
        place = random_generator.choices(places, weights=weights)[0]
        if place not in picked:
            picked.append(place)
        if len(picked) >= count:
            break
    return picked


def _build_journal_text(
    plan: dict,
    recommendations: list[dict],
    random_generator: random.Random,
) -> str:
    castle = plan["castle"]
    if random_generator.random() < 0.08:
        return random_generator.choice(SHORT_JOURNALS)

    lines = []
    previous_castle = plan["previous_castle"]
    if previous_castle is not None and random_generator.random() < 0.6:
        lines.append(
            random_generator.choice(
                [
                    (
                        f"上午去了{previous_castle.name}，下午接著來{castle.name}。"
                        if plan["same_day"]
                        else (
                            f"前一天去了{previous_castle.name}，"
                            f"今天接著來{castle.name}。"
                        )
                    ),
                    f"這趟城巡的第{plan['trip_index']}座城是{castle.name}。",
                ],
            ),
        )
    lines.append(random_generator.choice(SEASON_LINES[plan["travel_date"].month]))
    if random_generator.random() < 0.55:
        lines.append(
            random_generator.choice(ACCESS_LINES).format(
                minutes=random_generator.choice([5, 10, 15, 20, 25, 30]),
            ),
        )
    if castle.name in EXISTING_TENSHU_CASTLES:
        lines.append(random_generator.choice(EXISTING_TENSHU_LINES))
    elif castle.name in RECONSTRUCTED_TENSHU_CASTLES:
        lines.append(random_generator.choice(RECONSTRUCTED_TENSHU_LINES))
    else:
        lines.append(random_generator.choice(RUINS_LINES))
    if random_generator.random() < 0.6:
        stamp_lines = (
            STAMP_LINES if castle.castle_series == "original" else CONTINUED_STAMP_LINES
        )
        lines.append(
            random_generator.choice(stamp_lines).format(
                place=random_generator.choice(STAMP_PLACES),
            ),
        )
    if random_generator.random() < 0.45:
        lines.append(random_generator.choice(DURATION_LINES))
    if recommendations:
        lines.append(f"逛完之後順路去了{recommendations[0]['name']}。")
    lines.append(random_generator.choice(CLOSING_LINES))
    return "".join(line for line in lines if line)


def _build_recommendation_text(place: dict, random_generator: random.Random) -> str:
    template = random_generator.choice(RECOMMENDATION_LINES[place["category"]])
    return template.format(
        kind=place["kind"],
        minutes=max(3, round(place["distance"] / 80)),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(value))


def _load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
