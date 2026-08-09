import pandas as pd

from src.quality import validate_dataframe


PATIENT_IDS = {"P000001"}
PROCEDURE_CODES = {"PROC001"}
INSTITUTION_IDS = {"INST001"}


def create_valid_dataframe():
    return pd.DataFrame(
        [
            {
                "claim_id": "OA01-C000001",
                "patient_id": "P000001",
                "procedure_date": "2025-01-10",
                "procedure_code": "PROC001",
                "provider_id": "PRV0001",
                "institution_id": "INST001",
                "reimbursement_amount": 25.0,
                "patient_co_payment": 5.0,
                "quantity": 1,
                "accounting_year": 2025,
                "accounting_month": 2,
                "source_organisation": "OA01",
                "delivery_id": "OA01_2025_01",
            }
        ]
    )


def validate(df):
    return validate_dataframe(
        df=df,
        patient_ids=PATIENT_IDS,
        procedure_codes=PROCEDURE_CODES,
        institution_ids=INSTITUTION_IDS,
        delivery_id="TEST",
    )


def test_valid_record_has_no_issue():
    issues = validate(
        create_valid_dataframe()
    )

    assert issues.empty


def test_negative_reimbursement_is_detected():
    df = create_valid_dataframe()

    df.loc[
        0,
        "reimbursement_amount"
    ] = -10

    issues = validate(df)

    assert "DQ004" in set(
        issues["rule_id"]
    )


def test_unknown_institution_is_detected():
    df = create_valid_dataframe()

    df.loc[
        0,
        "institution_id"
    ] = "UNKNOWN"

    issues = validate(df)

    assert "DQ009" in set(
        issues["rule_id"]
    )


def test_missing_provider_is_warning():
    df = create_valid_dataframe()

    df.loc[
        0,
        "provider_id"
    ] = None

    issues = validate(df)

    provider_issue = issues[
        issues["rule_id"] == "DQ010"
    ]

    assert not provider_issue.empty
    assert (
        provider_issue.iloc[0]["severity"]
        == "WARNING"
    )