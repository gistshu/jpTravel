import sqlite3
from pathlib import Path

DB_PATH = Path("jp_travel.sqlite3")


def main() -> None:
    """Add image URL storage for castle journals."""
    connection = sqlite3.connect(DB_PATH)
    try:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(castle_journals)")
        }
        if "image_urls_json" not in columns:
            connection.execute(
                "ALTER TABLE castle_journals "
                "ADD COLUMN image_urls_json TEXT NOT NULL DEFAULT '[]'"
            )
            connection.commit()
            print("Added castle_journals.image_urls_json")
            return

        print("castle_journals.image_urls_json already exists")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
