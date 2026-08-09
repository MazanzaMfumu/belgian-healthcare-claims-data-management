# Data Model

```mermaid
erDiagram

    PATIENTS ||--o{ CLAIMS : generates
    PROCEDURES ||--o{ CLAIMS : classifies
    INSTITUTIONS ||--o{ CLAIMS : bills
    DELIVERIES ||--o{ CLAIMS : contains
    DELIVERIES ||--o{ DATA_QUALITY_ISSUES : generates