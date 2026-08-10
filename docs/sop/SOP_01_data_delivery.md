# SOP-01 — Data Delivery Management

## Purpose

Define the procedure for receiving and registering
synthetic healthcare data deliveries.

## Inputs

- Delivery CSV file
- Delivery manifest
- Data contract

## Procedure

1. Verify the expected filename.
2. Verify the source organisation.
3. Verify the reference period.
4. Check that the file exists.
5. Compare expected and actual row counts.
6. Validate mandatory columns.
7. Register the delivery status.
8. Forward valid deliveries to quality controls.
9. Place invalid deliveries in quarantine.
10. Record validation evidence.

## Acceptance criteria

A delivery may proceed only when all mandatory
structural requirements are satisfied.

## Evidence

- schema_validation.csv
- delivery_status.csv