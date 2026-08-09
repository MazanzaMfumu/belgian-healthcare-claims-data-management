from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
CONFIG_FILE = ROOT / "config" / "data_contract.yaml"
REPORT_DIR = ROOT / "outputs" / "quality_reports"


def load_required_columns():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        contract = yaml.safe_load(file)

    return contract["required_columns"]


def validate_columns(columns, required_columns):
    columns = set(columns)
    required = set(required_columns)

    missing = sorted(required - columns)
    unexpected = sorted(columns - required)

    return missing, unexpected


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    required_columns = load_required_columns()

    manifest = pd.read_csv(
        RAW_DIR / "delivery_manifest.csv"
    )

    results = []

    for _, delivery in manifest.iterrows():
        file_path = RAW_DIR / delivery["filename"]

        if not file_path.exists():
            results.append(
                {
                    "delivery_id": delivery["delivery_id"],
                    "filename": delivery["filename"],
                    "status": "FAIL",
                    "missing_columns": "",
                    "unexpected_columns": "",
                    "row_count_match": False,
                    "message": "File not found",
                }
            )
            continue

        df = pd.read_csv(file_path)

        missing, unexpected = validate_columns(
            df.columns,
            required_columns
        )

        status = "FAIL" if missing else "PASS"

        results.append(
            {
                "delivery_id": delivery["delivery_id"],
                "filename": delivery["filename"],
                "status": status,
                "missing_columns": ";".join(missing),
                "unexpected_columns": ";".join(unexpected),
                "row_count_match": (
                    len(df) == delivery["expected_rows"]
                ),
                "message": (
                    "Missing mandatory columns"
                    if missing
                    else "Schema valid"
                ),
            }
        )

    report = pd.DataFrame(results)

    report.to_csv(
        REPORT_DIR / "schema_validation.csv",
        index=False
    )

    print(report.to_string(index=False))


if __name__ == "__main__":
    main()