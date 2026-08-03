import argparse
import re
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

ORIGINAL_LIST_URL = "https://www.100finecastles.com/castles-list/"
ORIGINAL_MAP_URL = "https://www.100finecastles.com/castles-map/"
CONTINUED_LIST_URL = "https://www.100finecastles.com/castles-list2/"
CONTINUED_MAP_URL = "https://www.100finecastles.com/castles2nd-map/"
DATABASE_PATH = PROJECT_ROOT / "jp_travel.sqlite3"

SERIES_ORIGINAL = "original"
SERIES_CONTINUED = "continued"

NAME_TRANSLATION = str.maketrans(
    {
        "龜": "亀",
        "國": "国",
        "姬": "姫",
        "條": "条",
        "會": "会",
        "濱": "浜",
        "廣": "広",
        "澤": "沢",
        "邊": "辺",
        "隱": "隠",
        "樓": "楼",
        "ヶ": "ケ",
        "が": "ケ",
        "の": "",
        "跡": "",
        "群": "",
    }
)


@dataclass(frozen=True)
class OfficialCastle:
    number: int
    series: str
    name: str
    prefecture: str
    address: str
    latitude: float
    longitude: float
    source_url: str
    source_location_id: str


def main() -> None:
    """Import official Japan 100 and continued 100 castle metadata."""
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--original-list-html", type=Path)
    argument_parser.add_argument("--original-map-html", type=Path)
    argument_parser.add_argument("--continued-list-html", type=Path)
    argument_parser.add_argument("--continued-map-html", type=Path)
    args = argument_parser.parse_args()

    original_records = _build_records(
        list_html=_load_html(args.original_list_html, ORIGINAL_LIST_URL),
        map_html=_load_html(args.original_map_html, ORIGINAL_MAP_URL),
        list_url=ORIGINAL_LIST_URL,
        number_start=1,
        number_end=100,
        series=SERIES_ORIGINAL,
    )
    continued_records = _build_records(
        list_html=_load_html(args.continued_list_html, CONTINUED_LIST_URL),
        map_html=_load_html(args.continued_map_html, CONTINUED_MAP_URL),
        list_url=CONTINUED_LIST_URL,
        number_start=101,
        number_end=200,
        series=SERIES_CONTINUED,
    )

    _ensure_columns()
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        imported_count = _upsert_records(
            connection,
            original_records + continued_records,
        )
        connection.commit()
    finally:
        connection.close()

    print(
        f"Imported {imported_count} official castle records "
        f"({len(original_records)} original, {len(continued_records)} continued)."
    )


def _load_html(path: Path | None, url: str) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")

    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def _build_records(
    list_html: str,
    map_html: str,
    list_url: str,
    number_start: int,
    number_end: int,
    series: str,
) -> list[OfficialCastle]:
    list_entries = _parse_list_entries(list_html, list_url, number_start, number_end)
    pois_by_url, pois_by_name = _parse_map_pois(map_html)
    records = []
    for entry in list_entries:
        poi = pois_by_url.get(entry["href"]) or pois_by_name.get(
            _normalize_name(entry["name"])
        )
        if poi is None:
            raise RuntimeError(
                f"No map point found for {entry['number']} {entry['name']}"
            )

        records.append(
            OfficialCastle(
                number=entry["number"],
                series=series,
                name=entry["name"],
                prefecture=entry["prefecture"],
                address=poi["address"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                source_url=entry["href"],
                source_location_id=f"100finecastles-{entry['number']}",
            )
        )

    return records


def _parse_list_entries(
    html: str,
    base_url: str,
    number_start: int,
    number_end: int,
) -> list[dict[str, str | int]]:
    soup = BeautifulSoup(html, "html.parser")
    entries_by_number = {}
    for ordered_list in soup.find_all("ol"):
        start = int(ordered_list.get("start") or 1)
        for index, item in enumerate(ordered_list.find_all("li", recursive=False)):
            number = start + index
            if number < number_start or number > number_end:
                continue

            link = item.find("a", href=True)
            text = " ".join(item.get_text(" ", strip=True).split())
            match = re.match(r"^(.+?)（(.+?)）$", text)
            if link is None or match is None:
                continue

            entries_by_number.setdefault(
                number,
                {
                    "number": number,
                    "name": match.group(1).strip(),
                    "prefecture": _clean_prefecture(match.group(2)),
                    "href": urljoin(base_url, link["href"]),
                },
            )

    return [entries_by_number[number] for number in sorted(entries_by_number)]


def _parse_map_pois(
    html: str,
) -> tuple[dict[str, dict[str, str | float]], dict[str, dict[str, str | float]]]:
    soup = BeautifulSoup(html, "html.parser")
    pois_by_url = {}
    pois_by_name = {}
    for poi in soup.find_all("poi"):
        point = poi.get("point")
        title = (poi.get("title") or "").strip()
        link = poi.find("a", href=True)
        if point is None or not title or link is None:
            continue

        latitude_text, longitude_text = point.split(",", 1)
        record = {
            "name": title,
            "address": (poi.get("address") or "").strip(),
            "latitude": float(latitude_text),
            "longitude": float(longitude_text),
        }
        pois_by_url.setdefault(urljoin(ORIGINAL_LIST_URL, link["href"]), record)
        pois_by_name.setdefault(_normalize_name(title), record)

    return pois_by_url, pois_by_name


def _upsert_records(
    connection: sqlite3.Connection,
    records: list[OfficialCastle],
) -> int:
    connection.execute(
        "UPDATE castles SET castle_series = 'other', castle_number = NULL"
    )
    existing_castles = connection.execute(
        "SELECT id, name FROM castles ORDER BY id ASC"
    ).fetchall()
    existing_by_name = {
        _normalize_name(name): castle_id for castle_id, name in existing_castles
    }
    imported_count = 0
    for record in records:
        existing_id = _find_existing_castle_id(connection, record, existing_by_name)
        if existing_id is None:
            connection.execute(
                """
                INSERT INTO castles (
                    source_location_id,
                    name,
                    prefecture,
                    address,
                    latitude,
                    longitude,
                    image_url,
                    source_url,
                    castle_number,
                    castle_series,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, 'active')
                """,
                (
                    record.source_location_id,
                    record.name,
                    record.prefecture,
                    record.address,
                    record.latitude,
                    record.longitude,
                    record.source_url,
                    record.number,
                    record.series,
                ),
            )
        else:
            connection.execute(
                """
                UPDATE castles
                SET source_location_id = ?,
                    name = ?,
                    prefecture = ?,
                    address = ?,
                    latitude = ?,
                    longitude = ?,
                    source_url = ?,
                    castle_number = ?,
                    castle_series = ?
                WHERE id = ?
                """,
                (
                    record.source_location_id,
                    record.name,
                    record.prefecture,
                    record.address,
                    record.latitude,
                    record.longitude,
                    record.source_url,
                    record.number,
                    record.series,
                    existing_id,
                ),
            )
        imported_count += 1

    return imported_count


def _find_existing_castle_id(
    connection: sqlite3.Connection,
    record: OfficialCastle,
    existing_by_name: dict[str, int],
) -> int | None:
    by_number = connection.execute(
        """
        SELECT id FROM castles
        WHERE castle_number = ? AND castle_series = ?
        """,
        (record.number, record.series),
    ).fetchone()
    if by_number is not None:
        return int(by_number[0])

    by_source = connection.execute(
        "SELECT id FROM castles WHERE source_url = ?",
        (record.source_url,),
    ).fetchone()
    if by_source is not None:
        return int(by_source[0])

    return existing_by_name.get(_normalize_name(record.name))


def _ensure_columns() -> None:
    import scripts.migrate_add_castle_official_series as migration

    migration.main()


def _clean_prefecture(value: str) -> str:
    return re.split(r"[／/・]", value, maxsplit=1)[0].strip()


def _normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.translate(NAME_TRANSLATION)
    normalized = re.sub(r"[\\s・･()（）\\-ー]", "", normalized)
    return normalized


if __name__ == "__main__":
    main()
