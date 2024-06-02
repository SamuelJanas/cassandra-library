## Description
This is a simple library system implemented in Python using Tornado and Cassandra. 
The UI is implemented for the developer to test the system. The system allows for viewing books and reservations, making reservations, cancelling and updating them.

## How to use?
1. Run `docker-compose up --build seeder` to build and start the containers and populate the database with seeded data.
  Note: It's possible to generate random data by slightly modifying the `Dockerfile`. 
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
| reservation_id   | UUID      |             | Unique reservation identifier|
| book_id          | UUID      | Yes         | ID of the reserved book     |
| user_id          | INT       | Yes         | ID of the user making reservation |
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

#### Table: reservation_by_book_id
| Column           | Type      | Primary Key | Description                 |
|------------------|-----------|-------------|-----------------------------|
| book_id          | UUID      | Yes         | lock mechanism for concurrent requests |

## Testing
There is a separate script to run tests. You can run `python stress_test.py <test_number> --size <size> --workers <num_workers>` to run the apropriate test.
Short description of the tests:
- `1`: one user makes the same reservation `size` times
- `2`: `num_workers` clients make requests randomly (`size` times)
- `3`: Immediate occupancy of all reservations by 2 clients. You can set the number of books with `--size` flag
- `4`: Constant cancellations and book occupancy for the same book. (`size` 'cycles')
- `5`: Update `size` reservations concurrently using `num_workers` workers.

**Note**: there is a `unreserve_all.py` script to remove all reservations from the database. You can run it to 'reset' the database.

