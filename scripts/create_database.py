from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "placement_data.csv"
SCHEMA_PATH = ROOT / "database" / "schema.sql"
DB_PATH = ROOT / "placement_analytics.db"


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        df.to_sql("placements", conn, if_exists="append", index=False)

    print(f"Created database: {DB_PATH}")
    print(f"Loaded rows: {len(df)}")


if __name__ == "__main__":
    main()
