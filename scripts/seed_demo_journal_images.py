import argparse
import json
import random
import sqlite3
import uuid
from pathlib import Path

from PIL import Image, ImageDraw

DB_PATH = Path("jp_travel.sqlite3")
UPLOAD_ROOT = Path("static/uploads/journals")
MAX_STORED_IMAGE_BYTES = 1024 * 1024
DEFAULT_JOURNAL_COUNT = 50
RANDOM_SEED = 20260803

PALETTES = [
    ("#e9f1fb", "#b72f35", "#25313a"),
    ("#fff2cd", "#7a4e21", "#182026"),
    ("#eef3f1", "#2f7a5f", "#182026"),
    ("#f8dfdf", "#8e2731", "#25313a"),
    ("#dfe8ef", "#50606b", "#182026"),
]


def main() -> None:
    """Generate local demo image uploads for random journal records."""
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_JOURNAL_COUNT,
        help="Number of journal records to populate with demo images.",
    )
    argument_parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help="Random seed for deterministic local image generation.",
    )
    args = argument_parser.parse_args()

    random_generator = random.Random(args.seed)
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    try:
        journals = connection.execute(
            """
            SELECT cj.id, cj.castle_id, c.name, cj.travel_date
            FROM castle_journals AS cj
            JOIN castles AS c ON c.id = cj.castle_id
            WHERE cj.image_urls_json IS NULL OR cj.image_urls_json = '[]'
            ORDER BY cj.id ASC
            """
        ).fetchall()
        if not journals:
            print("No journals without images found.")
            return

        selected_journals = random_generator.sample(
            journals,
            min(args.count, len(journals)),
        )
        generated_file_count = 0
        for journal_id, castle_id, castle_name, travel_date in selected_journals:
            image_count = random_generator.randint(1, 5)
            image_urls = []
            for image_index in range(image_count):
                image_urls.append(
                    _create_demo_image(
                        random_generator=random_generator,
                        journal_id=journal_id,
                        castle_id=castle_id,
                        castle_name=castle_name,
                        travel_date=travel_date,
                        image_index=image_index,
                    )
                )
            generated_file_count += len(image_urls)
            connection.execute(
                """
                UPDATE castle_journals
                SET image_urls_json = ?
                WHERE id = ?
                """,
                (json.dumps(image_urls, ensure_ascii=False), journal_id),
            )

        connection.commit()
        print(
            f"Generated {generated_file_count} images "
            f"for {len(selected_journals)} journal records."
        )
    finally:
        connection.close()


def _create_demo_image(
    random_generator: random.Random,
    journal_id: int,
    castle_id: int,
    castle_name: str,
    travel_date: str,
    image_index: int,
) -> str:
    background, accent, ink = random_generator.choice(PALETTES)
    image = Image.new("RGB", (1280, 960), background)
    draw = ImageDraw.Draw(image)

    for _ in range(16):
        x0 = random_generator.randint(-140, 1120)
        y0 = random_generator.randint(-120, 840)
        x1 = x0 + random_generator.randint(120, 360)
        y1 = y0 + random_generator.randint(80, 280)
        draw.ellipse((x0, y0, x1, y1), fill=_soften_hex(accent, 0.22))

    draw.rectangle((76, 76, 1204, 884), outline=accent, width=12)
    draw.rectangle((104, 104, 1176, 856), outline="#ffffff", width=4)
    draw.polygon(
        [
            (250, 590),
            (640, 270),
            (1030, 590),
            (910, 590),
            (910, 720),
            (370, 720),
            (370, 590),
        ],
        fill=_soften_hex(accent, 0.78),
        outline=ink,
    )
    draw.rectangle((450, 500, 830, 720), fill="#ffffff", outline=ink, width=6)
    draw.rectangle((555, 410, 725, 500), fill="#ffffff", outline=ink, width=6)
    draw.line((220, 760, 1060, 760), fill=accent, width=8)

    label = f"Journal #{journal_id}"
    subtitle = f"Castle {castle_id} / {travel_date}"
    draw.text((128, 132), label, fill=ink)
    draw.text((128, 170), subtitle, fill=ink)
    draw.text((128, 808), f"{castle_name} image {image_index + 1}", fill=ink)

    filename = f"demo_{uuid.uuid4().hex}.jpg"
    output_path = UPLOAD_ROOT / filename
    _save_under_size_limit(image, output_path)
    return f"/static/uploads/journals/{filename}"


def _save_under_size_limit(image: Image.Image, output_path: Path) -> None:
    for quality in (86, 80, 74, 68, 62, 56):
        image.save(output_path, format="JPEG", quality=quality, optimize=True)
        if output_path.stat().st_size <= MAX_STORED_IMAGE_BYTES:
            return
    raise RuntimeError("Generated demo image exceeded 1MB.")


def _soften_hex(hex_color: str, opacity: float) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return (
        int(255 - (255 - red) * opacity),
        int(255 - (255 - green) * opacity),
        int(255 - (255 - blue) * opacity),
    )


if __name__ == "__main__":
    main()
