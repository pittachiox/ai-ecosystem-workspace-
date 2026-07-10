# Label Studio architecture

```mermaid
flowchart LR
  Browser[User Browser]
  LB[Label Studio (container)]
  PG[PostgreSQL (container)]
  Redis[Redis (container)]
  Volumes[(Volumes)]

  Browser -->|HTTP 8080| LB
  LB -->|JDBC/psycopg2| PG
  LB -->|cache/session| Redis
  PG --> Volumes
  Redis --> Volumes
  LB --> Volumes
```
