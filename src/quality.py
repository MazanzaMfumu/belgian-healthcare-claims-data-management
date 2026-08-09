import pandas as pd


ISSUE_COLUMNS = [
    "delivery_id",
    "rule_id",
    "severity",
    "claim_id",
    "field",
    "observed_value",
    "expected_value",
]


def validate_dataframe(
    df,
    patient_ids,
    procedure_codes,
    institution_ids,
    delivery_id,
):
    issues = []

    def add_issues(
        mask,
        rule_id,
        severity,
        field,
        expected,
    ):
        for index in df.index[mask]:
            issues.append(
                {
                    "delivery_id": delivery_id,
                    "rule_id": rule_id,
                    "severity": severity,
                    "claim_id": df.at[index, "claim_id"],
                    "field": field,
                    "observed_value": df.at[index, field],
                    "expected_value": expected,
                }
            )

    # DQ001
    mask = df["patient_id"].isna()
    add_issues(
        mask,
        "DQ001",
        "ERROR",
        "patient_id",
        "Non-null patient identifier",
    )

    # DQ002
    mask = df["claim_id"].duplicated(keep=False)
    add_issues(
        mask,
        "DQ002",
        "ERROR",
        "claim_id",
        "Unique claim identifier",
    )

    # DQ003
    dates = pd.to_datetime(
        df["procedure_date"],
        errors="coerce"
    )

    invalid_dates = dates.isna()

    add_issues(
        invalid_dates,
        "DQ003",
        "ERROR",
        "procedure_date",
        "Valid date",
    )

    future_dates = (
        dates > pd.Timestamp.today().normalize()
    ).fillna(False)

    add_issues(
        future_dates,
        "DQ003",
        "ERROR",
        "procedure_date",
        "Date must not be in the future",
    )

    # DQ004
    reimbursement = pd.to_numeric(
        df["reimbursement_amount"],
        errors="coerce"
    )

    mask = reimbursement.lt(0) | reimbursement.isna()

    add_issues(
        mask,
        "DQ004",
        "ERROR",
        "reimbursement_amount",
        "Numeric value greater than or equal to zero",
    )

    # DQ005
    copayment = pd.to_numeric(
        df["patient_co_payment"],
        errors="coerce"
    )

    mask = copayment.lt(0) | copayment.isna()

    add_issues(
        mask,
        "DQ005",
        "ERROR",
        "patient_co_payment",
        "Numeric value greater than or equal to zero",
    )

    # DQ006
    quantity = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    mask = quantity.le(0) | quantity.isna()

    add_issues(
        mask,
        "DQ006",
        "ERROR",
        "quantity",
        "Positive integer",
    )

    # DQ007
    mask = ~df["patient_id"].isin(patient_ids)

    add_issues(
        mask,
        "DQ007",
        "ERROR",
        "patient_id",
        "Known patient identifier",
    )

    # DQ008
    mask = ~df["procedure_code"].isin(
        procedure_codes
    )

    add_issues(
        mask,
        "DQ008",
        "ERROR",
        "procedure_code",
        "Known procedure code",
    )

    # DQ009
    mask = ~df["institution_id"].isin(
        institution_ids
    )

    add_issues(
        mask,
        "DQ009",
        "ERROR",
        "institution_id",
        "Known institution identifier",
    )

    # DQ010
    mask = df["provider_id"].isna()

    add_issues(
        mask,
        "DQ010",
        "WARNING",
        "provider_id",
        "Provider identifier should be available",
    )

    return pd.DataFrame(
        issues,
        columns=ISSUE_COLUMNS
    )