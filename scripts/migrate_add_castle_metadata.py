import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "jp_travel.sqlite3"


def main() -> None:
    """Add castle metadata columns used by the map UI."""
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(castles)")}
        if "prefecture" not in columns:
            connection.execute(
                "ALTER TABLE castles ADD COLUMN prefecture VARCHAR(32) "
                "NOT NULL DEFAULT ''"
            )
            print("Added castles.prefecture.")
        if "image_url" not in columns:
            connection.execute("ALTER TABLE castles ADD COLUMN image_url VARCHAR(500)")
            print("Added castles.image_url.")
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
