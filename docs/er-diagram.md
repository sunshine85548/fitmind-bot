\# ER Diagram



```mermaid

erDiagram



&#x20;   users {

&#x20;       INTEGER user\_id PK

&#x20;       TEXT username

&#x20;       REAL weight

&#x20;       REAL height

&#x20;       INTEGER age

&#x20;       TEXT gender

&#x20;       TEXT goal

&#x20;       REAL bmr

&#x20;   }



&#x20;   exercises {

&#x20;       INTEGER ex\_id PK

&#x20;       TEXT title

&#x20;       TEXT category

&#x20;       TEXT description

&#x20;       TEXT local\_path

&#x20;   }



&#x20;   activity\_logs {

&#x20;       INTEGER log\_id PK

&#x20;       INTEGER user\_id FK

&#x20;       INTEGER exercise\_id FK

&#x20;       DATETIME timestamp

&#x20;   }



&#x20;   user\_goals {

&#x20;       INTEGER goal\_id PK

&#x20;       INTEGER user\_id FK

&#x20;       TEXT title

&#x20;       BOOLEAN is\_completed

&#x20;   }



&#x20;   users ||--o{ activity\_logs : has

&#x20;   exercises ||--o{ activity\_logs : contains

&#x20;   users ||--o{ user\_goals : creates

```

