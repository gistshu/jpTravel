import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "jp_travel.sqlite3"


def main() -> None:
    """Rebuild castle_journals unique constraint to include travel_date."""
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list(castle_journals)")
        }
        if "sqlite_autoindex_castle_journals_1" not in indexes:
            print("castle_journals unique constraint already migrated.")
            return

        connection.execute("PRAGMA foreign_keys=off")
        connection.execute("BEGIN")
        connection.execute(
            """
            CREATE TABLE castle_journals_new (
                id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                castle_id INTEGER NOT NULL,
                visited BOOLEAN NOT NULL,
                journal_text TEXT NOT NULL,
                style VARCHAR(32) NOT NULL,
                created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
                created_by VARCHAR(64),
                updated_by VARCHAR(64),
                status VARCHAR(32) NOT NULL,
                travel_date DATE NOT NULL,
                PRIMARY KEY (id),
                CONSTRAINT uq_castle_journals_user_castle_date
                    UNIQUE (user_id, castle_id, travel_date),
                FOREIGN KEY(user_id) REFERENCES users (id),
                FOREIGN KEY(castle_id) REFERENCES castles (id)
            )
            """
        )
        connection.execute(
            """
            INSERT INTO castle_journals_new (
                id,
                user_id,
                castle_id,
                visited,
                journal_text,
                style,
                created_at,
                updated_at,
                created_by,
                updated_by,
                status,
                travel_date
            )
            SELECT
                id,
                user_id,
                castle_id,
                visited,
                journal_text,
                style,
                created_at,
                updated_at,
                created_by,
                updated_by,
                status,
                travel_date
            FROM castle_journals
            """
        )
        connection.execute("DROP TABLE castle_journals")
        connection.execute("ALTER TABLE castle_journals_new RENAME TO castle_journals")
        connection.execute(
            "CREATE INDEX ix_castle_journals_castle_id "
            "ON castle_journals (castle_id)"
        )
        connection.execute(
            "CREATE INDEX ix_castle_journals_status ON castle_journals (status)"
        )
        connection.execute(
            "CREATE INDEX ix_castle_journals_user_id ON castle_journals (user_id)"
        )
        connection.commit()
        print("Migrated castle_journals unique constraint to include travel_date.")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys=on")
        connection.close()


if __name__ == "__main__":
    main()
