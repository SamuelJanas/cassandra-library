## How to use?
1. Run `docker-compose up --build` to build and start the containers
2. Wait for the containers to start and populate the database with `docker-compose exec app python populate_books.py`
3. `docker-compose exec app /bin/sh` to enter containers shell, run `python app.py` to start the app.
4. Open your browser and go to `http://localhost:5000/` to see the app running.

---
To access cqlsh, run `docker-compose exec <container-name> cqlsh` in your terminal.