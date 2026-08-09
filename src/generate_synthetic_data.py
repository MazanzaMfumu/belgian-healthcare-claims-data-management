from pathlib import Path
from datetime import date, timedelta
import random

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REFERENCE_DIR = ROOT / "data" / "reference"
SAMPLE_DIR = ROOT / "data" / "sample"

RNG = random.Random(42)

RAW_DIR.mkdir(parents=True, exist_ok=True)
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def create_reference_data():
    patients = pd.DataFrame(
        {
            "patient_id": [f"P{i:06d}" for i in range(1, 2001)],
            "birth_year": [RNG.randint(1935, 2005) for _ in range(2000)],
            "sex": [RNG.choice(["F", "M"]) for _ in range(2000)],
            "region": [
                RNG.choice(["Brussels", "Flanders", "Wallonia"])
                for _ in range(2000)
            ],
            "increased_reimbursement": [
                RNG.choice([0, 1]) for _ in range(2000)
            ],
        }
    )

    procedures = pd.DataFrame(
        {
            "procedure_code": [f"PROC{i:03d}" for i in range(1, 21)],
            "procedure_label": [
                f"Synthetic procedure {i}" for i in range(1, 21)
            ],
        }
    )

    institutions = pd.DataFrame(
        {
            "institution_id": [f"INST{i:03d}" for i in range(1, 31)],
            "institution_type": [
                RNG.choice(["Hospital", "Clinic", "Primary care"])
                for _ in range(30)
            ],
        }
    )

    patients.to_csv(REFERENCE_DIR / "patients.csv", index=False)
    procedures.to_csv(REFERENCE_DIR / "procedures.csv", index=False)
    institutions.to_csv(REFERENCE_DIR / "institutions.csv", index=False)

    return patients, procedures, institutions


def create_claims():
    patients, procedures, institutions = create_reference_data()

    patient_ids = patients["patient_id"].tolist()
    procedure_codes = procedures["procedure_code"].tolist()
    institution_ids = institutions["institution_id"].tolist()

    manifest = []
    sample_frames = []

    start_date = date(2025, 1, 1)

    for organisation_number in range(1, 8):
        organisation = f"OA{organisation_number:02d}"
        delivery_id = f"{organisation}_2025_01"

        records = []

        for row_number in range(1, 1001):
            service_date = start_date + timedelta(
                days=RNG.randint(0, 364)
            )

            accounting_date = service_date + timedelta(
                days=RNG.randint(1, 90)
            )

            records.append(
                {
                    "claim_id": f"{organisation}-C{row_number:06d}",
                    "patient_id": RNG.choice(patient_ids),
                    "procedure_date": service_date.isoformat(),
                    "procedure_code": RNG.choice(procedure_codes),
                    "provider_id": f"PRV{RNG.randint(1, 300):04d}",
                    "institution_id": RNG.choice(institution_ids),
                    "reimbursement_amount": round(
                        RNG.uniform(5, 300), 2
                    ),
                    "patient_co_payment": round(
                        RNG.uniform(0, 50), 2
                    ),
                    "quantity": RNG.randint(1, 3),
                    "accounting_year": accounting_date.year,
                    "accounting_month": accounting_date.month,
                    "source_organisation": organisation,
                    "delivery_id": delivery_id,
                }
            )

        df = pd.DataFrame(records)

        # Intentional data-quality problems
        if organisation == "OA02":
            df.loc[:9, "provider_id"] = None

        elif organisation == "OA03":
            df = pd.concat(
                [df, df.iloc[:5]],
                ignore_index=True
            )

        elif organisation == "OA04":
            df.loc[:4, "reimbursement_amount"] = -25.00

        elif organisation == "OA05":
            df.loc[:4, "procedure_date"] = "2030-01-15"

        elif organisation == "OA06":
            df.loc[:4, "institution_id"] = "INST999"

        elif organisation == "OA07":
            df = df.drop(columns=["patient_co_payment"])

        filename = f"{organisation}_2025_01.csv"
        df.to_csv(RAW_DIR / filename, index=False)

        manifest.append(
            {
                "delivery_id": delivery_id,
                "source_organisation": organisation,
                "reference_period": "2025-01",
                "filename": filename,
                "expected_rows": 1000,
                "actual_rows": len(df),
            }
        )

        sample_frames.append(df.head(5))

    pd.DataFrame(manifest).to_csv(
        RAW_DIR / "delivery_manifest.csv",
        index=False
    )

    pd.concat(
        sample_frames,
        ignore_index=True
    ).to_csv(
        SAMPLE_DIR / "claims_sample.csv",
        index=False
    )


if __name__ == "__main__":
    create_claims()
    print("Synthetic healthcare deliveries created successfully.")