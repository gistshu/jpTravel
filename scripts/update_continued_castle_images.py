import argparse
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

DATABASE_PATH = PROJECT_ROOT / "jp_travel.sqlite3"


def main() -> None:
    """Update continued 100 castle images from their detail pages."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist image URLs. Without this flag, only prints a dry-run summary.",
    )
    args = parser.parse_args()

    connection = sqlite3.connect(DATABASE_PATH)
    try:
        castles = connection.execute(
            """
            SELECT id, castle_number, name, source_url, image_url
            FROM castles
            WHERE castle_series = 'continued'
            ORDER BY castle_number ASC
            """
        ).fetchall()
        updates = []
        missing = []
        for castle_id, number, name, source_url, current_image_url in castles:
            image_url = _extract_first_castle_image(source_url)
            if image_url is None:
                missing.append((number, name, source_url))
                continue
            if image_url != current_image_url:
                updates.append((castle_id, number, name, image_url))

        print(f"Found {len(updates)} continued castle image updates.")
        if missing:
            print(f"Missing images: {len(missing)}")
            for number, name, source_url in missing[:20]:
                print(f"- #{number} {name}: {source_url}")

        if not args.apply:
            print("Dry-run only. Re-run with --apply to update SQLite.")
            return

        for castle_id, _number, _name, image_url in updates:
            connection.execute(
                "UPDATE castles SET image_url = ? WHERE id = ?",
                (image_url, castle_id),
            )
        connection.commit()
        print(f"Updated {len(updates)} continued castle image URLs.")
    finally:
        connection.close()


def _extract_first_castle_image(source_url: str) -> str | None:
    with urlopen(source_url, timeout=30) as response:
        html = response.read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    for image in soup.find_all("img"):
        image_url = image.get("data-src") or image.get("src")
        if not image_url:
            continue
        if "/wordpress/wp-content/uploads/" not in image_url:
            continue
        return urljoin(source_url, image_url)

    return None


if __name__ == "__main__":
    main()
