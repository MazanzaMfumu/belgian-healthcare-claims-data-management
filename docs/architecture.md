# Architecture

```mermaid
flowchart TD

A[Source organisations OA01-OA07]
--> B[Raw deliveries]

B --> C[Schema validation]

C --> D{Schema valid?}

D -- No --> E[Quarantine]

D -- Yes --> F[Data quality controls]

F --> G{Blocking issues?}

G -- Yes --> E

G -- No --> H[Accepted deliveries]

H --> I[ETL transformation]

I --> J[DuckDB database]

J --> K[Controlled SQL extraction]

K --> L[Delivery to authorised user]

F --> M[Quality reports]

M --> N[Incident management]