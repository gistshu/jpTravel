import sqlite3
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

DATABASE_PATH = PROJECT_ROOT / "jp_travel.sqlite3"


def main() -> None:
    """Add required travel_date column to castle_journals when missing."""
    today = date.today().isoformat()
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(castle_journals)")
        }
        if "travel_date" in columns:
            print("travel_date column already exists.")
            return

        connection.execute(
            "ALTER TABLE castle_journals "
            f"ADD COLUMN travel_date DATE NOT NULL DEFAULT '{today}'"
        )
        connection.commit()
        print(f"Added travel_date column with default {today}.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
