from pathlib import Path
import shutil

import pandas as pd

from src.quality import validate_dataframe


ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
REFERENCE_DIR = ROOT / "data" / "reference"
INTERIM_DIR = ROOT / "data" / "interim"
QUARANTINE_DIR = ROOT / "data" / "quarantine"

REPORT_DIR = ROOT / "outputs" / "quality_reports"


def clear_generated_csv(folder):
    folder.mkdir(parents=True, exist_ok=True)

    for file_path in folder.glob("*.csv"):
        file_path.unlink()


def main():
    clear_generated_csv(INTERIM_DIR)
    clear_generated_csv(QUARANTINE_DIR)

    schema_report = pd.read_csv(
        REPORT_DIR / "schema_validation.csv"
    )

    patients = pd.read_csv(
        REFERENCE_DIR / "patients.csv"
    )

    procedures = pd.read_csv(
        REFERENCE_DIR / "procedures.csv"
    )

    institutions = pd.read_csv(
        REFERENCE_DIR / "institutions.csv"
    )

    patient_ids = set(patients["patient_id"])
    procedure_codes = set(
        procedures["procedure_code"]
    )
    institution_ids = set(
        institutions["institution_id"]
    )

    all_issues = []
    delivery_statuses = []

    for _, row in schema_report.iterrows():
        delivery_id = row["delivery_id"]
        filename = row["filename"]
        source_file = RAW_DIR / filename

        if row["status"] == "FAIL":
            shutil.copy2(
                source_file,
                QUARANTINE_DIR / filename
            )

            delivery_statuses.append(
                {
                    "delivery_id": delivery_id,
                    "filename": filename,
                    "status": "REJECTED_SCHEMA",
                    "blocking_issues": 1,
                    "warnings": 0,
                }
            )
            continue

        df = pd.read_csv(source_file)

        issues = validate_dataframe(
            df=df,
            patient_ids=patient_ids,
            procedure_codes=procedure_codes,
            institution_ids=institution_ids,
            delivery_id=delivery_id,
        )

        if not issues.empty:
            all_issues.append(issues)

        blocking = issues[
            issues["severity"] == "ERROR"
        ]

        warnings = issues[
            issues["severity"] == "WARNING"
        ]

        if not blocking.empty:
            shutil.copy2(
                source_file,
                QUARANTINE_DIR / filename
            )

            status = "REJECTED_QUALITY"

        else:
            df.to_csv(
                INTERIM_DIR
                / filename.replace(
                    ".csv",
                    "_accepted.csv"
                ),
                index=False,
            )

            status = "ACCEPTED"

        delivery_statuses.append(
            {
                "delivery_id": delivery_id,
                "filename": filename,
                "status": status,
                "blocking_issues": len(blocking),
                "warnings": len(warnings),
            }
        )

    if all_issues:
        issue_report = pd.concat(
            all_issues,
            ignore_index=True
        )
    else:
        issue_report = pd.DataFrame()

    issue_report.to_csv(
        REPORT_DIR / "data_quality_issues.csv",
        index=False
    )

    status_report = pd.DataFrame(
        delivery_statuses
    )

    status_report.to_csv(
        REPORT_DIR / "delivery_status.csv",
        index=False
    )

    print(status_report.to_string(index=False))


if __name__ == "__main__":
    main()