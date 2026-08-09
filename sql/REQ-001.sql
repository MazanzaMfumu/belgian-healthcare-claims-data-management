SELECT
    c.claim_id,
    c.patient_id,
    c.sex,
    c.region,
    c.procedure_date,
    c.procedure_code,
    c.procedure_label,
    c.reimbursement_amount,
    c.patient_co_payment

FROM vw_claims_enriched c

WHERE
    EXTRACT(YEAR FROM c.procedure_date) = 2025
    AND (2025 - c.birth_year) >= 65

ORDER BY
    c.procedure_date,
    c.claim_id;