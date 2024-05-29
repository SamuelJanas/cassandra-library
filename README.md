## How to use?
1. Run `docker-compose up --build seeder` to build and start the containers and populate the databse
2. Run `docker-compose up --build app` to build containers and run the app
3. Open your browser and go to `http://localhost:8888/` to see the app running.

---
To access cqlsh, run `docker-compose exec <container-name> cqlsh` in your terminal.


## Schema 
### Keyspace: library
- Replication Strategy: NetworkTopologyStrategy
  - Datacenter1: 3

#### Table: books
| Column          | Type  | Primary Key | Description          |
|-----------------|-------|-------------|----------------------|
| book_id         | UUID  | Yes         | Unique identifier   |
| title           | TEXT  |             | Title of the book    |
| author          | TEXT  |             | Author of the book   |
| genre           | TEXT  |             | Genre of the book    |
| published_year  | INT   |             | Year of publication  |

#### Table: reservations
| Column           | Type      | Primary Key | Description                 |
|------------------|-----------|-------------|-----------------------------|
| reservation_id   | UUID      | Yes         | Unique reservation identifier|
| book_id          | UUID      |             | ID of the reserved book     |
| user_id          | INT       |             | ID of the user making reservation |
| reserved_at      | TIMESTAMP |             | Timestamp of reservation    |

#### Table: user_reservations
| Column           | Type      | Primary Key | Description                 |
|------------------|-----------|-------------|-----------------------------|
| user_id          | INT       | Yes         | User ID                     |
| reservation_id   | UUID      | Yes         | Reservation ID              |
| book_id          | UUID      |             | ID of the reserved book     |
| reserved_at      | TIMESTAMP |             | Timestamp of reservation    |

#### Table: book_reservations
| Column           | Type      | Primary Key | Description                 |
|------------------|-----------|-------------|-----------------------------|
| book_id          | UUID      | Yes         | Book ID                     |
| reservation_id   | UUID      | Yes         | Reservation ID              |
| user_id          | INT       |             | ID of the user making reservation |
| reserved_at      | TIMESTAMP |             | Timestamp of reservation    |