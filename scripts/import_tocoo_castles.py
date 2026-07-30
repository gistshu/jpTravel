import argparse
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

SOURCE_URL = "https://www2.tocoo.jp/must-visit/fine-castles.php?cc=cn"


def load_source_html(path: Path | None) -> str:
    """Load ToCoo HTML from a local file or the source URL."""
    if path is not None:
        return path.read_text(encoding="utf-8")

    with urlopen(SOURCE_URL, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_castles(html: str) -> list[dict[str, str | float]]:
    """Parse castle records from ToCoo HTML."""
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, str | float]] = []

    for district_element in soup.select("section.skr-distWrap"):
        prefecture_element = district_element.select_one("h3.skr-dist")
        prefecture = (
            prefecture_element.get_text(strip=True)
            if prefecture_element is not None
            else ""
        )

        for castle_element in district_element.select("li.skr-spot"):
            record = _parse_castle_element(castle_element, prefecture)
            if record is not None:
                records.append(record)

    return records


def _parse_castle_element(
    castle_element: Any,
    prefecture: str,
) -> dict[str, str | float] | None:
    name_element = castle_element.select_one("h4.skr-spotmi")
    map_element = castle_element.select_one("a.remodalMap")
    if name_element is None or map_element is None:
        return None

    source_location_id = castle_element.get("id")
    latitude = map_element.get("data-lat")
    longitude = map_element.get("data-lng")
    if source_location_id is None or latitude is None or longitude is None:
        return None

    return {
        "source_location_id": source_location_id,
        "name": name_element.get_text(strip=True),
        "prefecture": prefecture,
        "address": _extract_address(map_element),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "image_url": _extract_image_url(castle_element),
    }


def import_castles(db_session: Any, records: list[dict[str, str | float]]) -> int:
    """Persist parsed castle records to SQLite."""
    from app.models.castle import Castle
    from app.repositories.castle_repository import CastleRepository

    castles = [
        Castle(
            source_location_id=str(record["source_location_id"]),
            name=str(record["name"]),
            prefecture=str(record["prefecture"]),
            address=str(record["address"]),
            latitude=float(record["latitude"]),
            longitude=float(record["longitude"]),
            image_url=str(record["image_url"]) or None,
            source_url=SOURCE_URL,
        )
        for record in records
    ]
    repository = CastleRepository(db_session)
    affected_count = repository.upsert_many(castles)
    db_session.commit()
    return affected_count


def _extract_address(map_element: Any) -> str:
    raw_address = map_element.previous_sibling
    if raw_address is None:
        return ""

    address = str(raw_address)
    address = re.sub(r"\s*\($", "", address)
    return re.sub(r"\s+", " ", address).strip()


def _extract_image_url(castle_element: Any) -> str:
    image_element = castle_element.select_one("img.skr-spotImg")
    if image_element is None:
        return ""

    source = image_element.get("data-src") or image_element.get("src") or ""
    return urljoin(SOURCE_URL, str(source))


def main() -> None:
    """Import ToCoo castle coordinates into SQLite."""
    from app.core.database import SessionLocal, create_database_tables

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--html", type=Path, default=None)
    args = argument_parser.parse_args()

    html = load_source_html(args.html)
    records = parse_castles(html)
    if not records:
        raise RuntimeError("No castle records were parsed from ToCoo HTML.")

    create_database_tables()
    db_session = SessionLocal()
    try:
        affected_count = import_castles(db_session, records)
    finally:
        db_session.close()

    print(f"Imported {affected_count} castle records.")


if __name__ == "__main__":
    main()
