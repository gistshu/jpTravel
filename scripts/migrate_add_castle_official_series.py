import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "jp_travel.sqlite3"


def main() -> None:
    """Add official 100/continued 100 castle metadata columns."""
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(castles)")}
        if "castle_number" not in columns:
            connection.execute("ALTER TABLE castles ADD COLUMN castle_number INTEGER")
            print("Added castles.castle_number.")
        if "castle_series" not in columns:
            connection.execute(
                "ALTER TABLE castles ADD COLUMN castle_series VARCHAR(32) "
                "NOT NULL DEFAULT 'other'"
            )
            print("Added castles.castle_series.")
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
