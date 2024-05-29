## How to use?
1. Run `docker-compose up --build seeder` to build and start the containers and populate the databse
2. Run `docker-compose up --build app` to build containers and run the app
3. Open your browser and go to `http://localhost:8888/` to see the app running.

---
To access cqlsh, run `docker-compose exec <container-name> cqlsh` in your terminal.