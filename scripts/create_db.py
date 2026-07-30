import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


def main() -> None:
    """Create local database tables."""
    from app.core.database import create_database_tables

    create_database_tables()


if __name__ == "__main__":
    main()
