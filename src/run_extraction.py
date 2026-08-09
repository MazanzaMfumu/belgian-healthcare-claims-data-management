from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

import duckdb


ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    ROOT
    / "database"
    / "healthcare_claims.duckdb"
)

SQL_FILE = (
    ROOT
    / "sql"
    / "REQ-001.sql"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "extracts"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "REQ-001.csv"
)

METADATA_FILE = (
    OUTPUT_DIR
    / "REQ-001_metadata.json"
)


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    sql = SQL_FILE.read_text(
        encoding="utf-8"
    )

    connection = duckdb.connect(
        str(DATABASE_FILE),
        read_only=True
    )

    result = connection.execute(
        sql
    ).fetchdf()

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    checksum = hashlib.sha256(
        OUTPUT_FILE.read_bytes()
    ).hexdigest()

    metadata = {
        "request_id": "REQ-001",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "row_count": len(result),
        "sql_file": "sql/REQ-001.sql",
        "output_file": "outputs/extracts/REQ-001.csv",
        "sha256": checksum,
    }

    METADATA_FILE.write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8",
    )

    connection.close()

    print(
        f"Controlled extract created: "
        f"{len(result)} rows"
    )


if __name__ == "__main__":
    main()