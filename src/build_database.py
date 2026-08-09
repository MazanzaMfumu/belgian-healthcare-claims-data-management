from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INTERIM_DIR = ROOT / "data" / "interim"
REFERENCE_DIR = ROOT / "data" / "reference"
REPORT_DIR = ROOT / "outputs" / "quality_reports"
DATABASE_DIR = ROOT / "database"

DATABASE_FILE = (
    DATABASE_DIR / "healthcare_claims.duckdb"
)


def main():
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    accepted_files = list(
        INTERIM_DIR.glob("*_accepted.csv")
    )

    if not accepted_files:
        raise RuntimeError(
            "No accepted deliveries found."
        )

    claims = pd.concat(
        [
            pd.read_csv(file)
            for file in accepted_files
        ],
        ignore_index=True,
    )

    claims["procedure_date"] = pd.to_datetime(
        claims["procedure_date"]
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

    deliveries = pd.read_csv(
        REPORT_DIR / "delivery_status.csv"
    )

    issues_file = (
        REPORT_DIR / "data_quality_issues.csv"
    )

    issues = pd.read_csv(issues_file)

    connection = duckdb.connect(
        str(DATABASE_FILE)
    )

    connection.register(
        "claims_df",
        claims
    )

    connection.register(
        "patients_df",
        patients
    )

    connection.register(
        "procedures_df",
        procedures
    )

    connection.register(
        "institutions_df",
        institutions
    )

    connection.register(
        "deliveries_df",
        deliveries
    )

    connection.register(
        "issues_df",
        issues
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE claims AS
        SELECT * FROM claims_df
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE patients AS
        SELECT * FROM patients_df
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE procedures AS
        SELECT * FROM procedures_df
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE institutions AS
        SELECT * FROM institutions_df
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE deliveries AS
        SELECT * FROM deliveries_df
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE
        data_quality_issues AS
        SELECT * FROM issues_df
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE VIEW
        vw_claims_enriched AS

        SELECT
            c.*,
            p.birth_year,
            p.sex,
            p.region,
            p.increased_reimbursement,
            pr.procedure_label,
            i.institution_type

        FROM claims c

        LEFT JOIN patients p
            USING(patient_id)

        LEFT JOIN procedures pr
            USING(procedure_code)

        LEFT JOIN institutions i
            USING(institution_id)
        """
    )

    tables = connection.execute(
        "SHOW TABLES"
    ).fetchdf()

    print(tables.to_string(index=False))

    print(
        "\nClaims loaded:",
        connection.execute(
            "SELECT COUNT(*) FROM claims"
        ).fetchone()[0],
    )

    connection.close()


if __name__ == "__main__":
    main()