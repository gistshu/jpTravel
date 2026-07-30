import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

SOURCE_URL = "https://zh.wikipedia.org/wiki/日本100名城"

VARIANT_CHARACTERS = str.maketrans(
    {
        "会": "會",
        "亀": "龜",
        "彦": "彥",
        "姫": "姬",
        "浜": "濱",
        "広": "廣",
        "戸": "戶",
        "条": "條",
        "国": "國",
        "発": "發",
        "乗": "乘",
        "冈": "岡",
        "泽": "澤",
        "户": "戶",
        "县": "縣",
    }
)

CAPTION_ALIASES = {
    "若松城": "會津若松城",
    "朝倉氏館跡": "一乘谷城",
    "金山城": "新田金山城",
    "武田氏館": "武田氏館",
}

PREFECTURES = [
    "北海道",
    "青森縣",
    "岩手縣",
    "宮城縣",
    "秋田縣",
    "山形縣",
    "福島縣",
    "茨城縣",
    "栃木縣",
    "群馬縣",
    "埼玉縣",
    "千葉縣",
    "東京都",
    "神奈川縣",
    "新潟縣",
    "富山縣",
    "石川縣",
    "福井縣",
    "山梨縣",
    "長野縣",
    "岐阜縣",
    "靜岡縣",
    "愛知縣",
    "三重縣",
    "滋賀縣",
    "京都府",
    "大阪府",
    "兵庫縣",
    "奈良縣",
    "和歌山縣",
    "鳥取縣",
    "島根縣",
    "岡山縣",
    "廣島縣",
    "山口縣",
    "德島縣",
    "香川縣",
    "愛媛縣",
    "高知縣",
    "福岡縣",
    "佐賀縣",
    "長崎縣",
    "熊本縣",
    "大分縣",
    "宮崎縣",
    "鹿兒島縣",
    "沖繩縣",
]


@dataclass(frozen=True)
class WikipediaCastleImage:
    name: str
    prefecture: str
    image_url: str


def load_source_html(path: Path | None) -> str:
    """Load Wikipedia HTML from a local file or the source URL."""
    if path is not None:
        return path.read_text(encoding="utf-8")

    with urlopen(SOURCE_URL, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_wikipedia_castle_images(html: str) -> list[WikipediaCastleImage]:
    """Parse castle image URLs from the Japanese 100 castles Wikipedia page."""
    soup = BeautifulSoup(html, "html.parser")
    content = (
        soup.select_one(".mw-parser-output")
        or soup.select_one("#mw-content-text")
        or soup
    )
    records: list[WikipediaCastleImage] = []

    for section_nodes in _iter_content_sections(content):
        castles = _parse_section_castles(section_nodes)
        if not castles:
            continue

        castle_by_name = {_normalize_name(castle["name"]): castle for castle in castles}
        for gallery in (node for node in section_nodes if _has_class(node, "gallery")):
            for image_item in gallery.select("li.gallerybox"):
                parsed_image = _parse_gallery_image(image_item)
                if parsed_image is None:
                    continue

                caption, image_url = parsed_image
                castle = _match_gallery_caption(caption, castle_by_name)
                if castle is None:
                    continue

                records.append(
                    WikipediaCastleImage(
                        name=castle["name"],
                        prefecture=castle["prefecture"],
                        image_url=image_url,
                    )
                )

    return records


def update_castle_images(
    db_session: Any,
    records: list[WikipediaCastleImage],
    *,
    apply_changes: bool,
) -> tuple[int, list[str]]:
    """Update local castle image URLs from parsed Wikipedia image records."""
    from sqlalchemy import select

    from app.models.castle import Castle

    wikipedia_images = {
        (_normalize_name(record.name), _normalize_prefecture(record.prefecture)): record
        for record in records
    }
    castles = list(db_session.scalars(select(Castle).order_by(Castle.id.asc())).all())
    unmatched_names: list[str] = []
    update_count = 0

    for castle in castles:
        key = (_normalize_name(castle.name), _normalize_prefecture(castle.prefecture))
        record = wikipedia_images.get(key)
        if record is None:
            unmatched_names.append(f"{castle.name} ({castle.prefecture})")
            continue

        if castle.image_url != record.image_url:
            update_count += 1
            if apply_changes:
                castle.image_url = record.image_url

    if apply_changes:
        db_session.commit()
    else:
        db_session.rollback()

    return update_count, unmatched_names


def _iter_content_sections(content: Any) -> list[list[Any]]:
    sections: list[list[Any]] = []
    current_section: list[Any] = []

    for node in content.children:
        if not getattr(node, "name", None):
            continue

        if _is_level_two_heading(node):
            if current_section:
                sections.append(current_section)
            current_section = []
            continue

        current_section.append(node)

    if current_section:
        sections.append(current_section)

    return sections


def _is_level_two_heading(node: Any) -> bool:
    if node.name == "h2":
        return True
    return _has_class(node, "mw-heading2")


def _parse_section_castles(nodes: list[Any]) -> list[dict[str, str]]:
    castles: list[dict[str, str]] = []
    current_prefecture = ""

    for table in (node for node in nodes if node.name == "table"):
        for row in table.select("tr"):
            cells = row.select("td")
            if len(cells) < 2:
                continue

            name = _extract_cell_name(cells[1])
            if not name:
                continue

            prefecture = _extract_prefecture_from_row(cells) or current_prefecture
            if prefecture:
                current_prefecture = prefecture

            castles.append({"name": name, "prefecture": prefecture})

    return castles


def _extract_cell_name(cell: Any) -> str:
    link = cell.select_one("a[title]")
    text = (
        link.get_text(strip=True)
        if link is not None
        else cell.get_text(" ", strip=True)
    )
    return _clean_castle_name(text)


def _extract_prefecture_from_row(cells: list[Any]) -> str:
    for cell in cells[2:]:
        text = _normalize_prefecture(cell.get_text(" ", strip=True))
        for prefecture in PREFECTURES:
            if prefecture in text:
                return prefecture
    return ""


def _parse_gallery_image(image_item: Any) -> tuple[str, str] | None:
    image = image_item.select_one("img")
    caption_element = image_item.select_one(".gallerytext")
    if image is None or caption_element is None:
        return None

    caption = _clean_castle_name(caption_element.get_text(" ", strip=True))
    image_url = _extract_largest_image_url(image)
    if not caption or not image_url:
        return None

    return caption, image_url


def _extract_largest_image_url(image: Any) -> str:
    srcset = image.get("srcset")
    if srcset:
        candidates = [
            candidate.strip().split(" ")[0] for candidate in srcset.split(",")
        ]
        if candidates:
            return _absolute_url(candidates[-1])

    source = image.get("src") or ""
    return _absolute_url(str(source))


def _match_gallery_caption(
    caption: str,
    castle_by_name: dict[str, dict[str, str]],
) -> dict[str, str] | None:
    normalized_caption = _normalize_name(CAPTION_ALIASES.get(caption, caption))
    exact_match = castle_by_name.get(normalized_caption)
    if exact_match is not None:
        return exact_match

    for castle_name, castle in castle_by_name.items():
        if normalized_caption.startswith(castle_name) or castle_name.startswith(
            normalized_caption
        ):
            return castle

    return None


def _clean_castle_name(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[（(].*?[）)]", "", text)
    return text.split("・", 1)[0].strip()


def _normalize_name(name: str) -> str:
    return _clean_castle_name(name).translate(VARIANT_CHARACTERS)


def _normalize_prefecture(prefecture: str) -> str:
    return prefecture.translate(VARIANT_CHARACTERS).replace("県", "縣").strip()


def _absolute_url(url: str) -> str:
    if url.startswith("//"):
        return f"https:{url}"
    return urljoin(SOURCE_URL, url)


def _has_class(node: Any, class_name: str) -> bool:
    classes = node.get("class") if hasattr(node, "get") else None
    return classes is not None and class_name in classes


def main() -> None:
    """Update local castle images from Wikipedia gallery images."""
    from app.core.database import SessionLocal

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--html", type=Path, default=None)
    argument_parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to the local SQLite database.",
    )
    args = argument_parser.parse_args()

    html = load_source_html(args.html)
    records = parse_wikipedia_castle_images(html)
    if not records:
        raise RuntimeError("No Wikipedia castle image records were parsed.")

    db_session = SessionLocal()
    try:
        update_count, unmatched_names = update_castle_images(
            db_session,
            records,
            apply_changes=args.apply,
        )
    finally:
        db_session.close()

    action = "Updated" if args.apply else "Would update"
    print(f"Parsed {len(records)} Wikipedia image records.")
    print(f"{action} {update_count} castle image URLs.")
    if unmatched_names:
        print("Unmatched local castles:")
        for castle_name in unmatched_names:
            print(f"- {castle_name}")


if __name__ == "__main__":
    main()
