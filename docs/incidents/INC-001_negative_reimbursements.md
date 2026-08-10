# INC-001 — Negative reimbursement amounts

## Incident

The synthetic OA04 delivery contains negative
reimbursement amounts.

## Detection

Rule DQ004 detected reimbursement amounts
below zero.

## Impact

The affected delivery cannot be loaded into
the validated healthcare claims database.

## Decision

Delivery rejected and moved to quarantine.

## Corrective action

The source organisation would be requested
to verify the sign convention and submit
a corrected delivery.

## Preventive action

DQ004 remains part of the automated
financial validation rules.

## Status

Resolved in synthetic demonstration.