# UniHostel

A hostel booking platform (BACKEND ONLY)

End of year project for Group 2

## Group members

1. EBIL PAUL 2023/DCS/DAY/0257
2. OCEPA HARON 2023/DCS/DAY/0522
3. NASSALI MONICA 2023/DCS/DAY/1557
4. OPIO EMMANUEL NICHOLAS 2023/DCS/DAY/0248

## TECH STACK

- [FastAPI](https://fastapi.tiangolo.com/) - Python backend framework
- [Next.js](https://nextjs.org/) - Javascript frontend framework
- [SqlAlchemy](https://www.sqlalchemy.org/) - Python ORM for sql databases
- [Postgresql](https://www.postgresql.org/) - SQL database
- [Minio](http://min.io/) - Object Storage 
- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) - Python Database migration tool

### How to run the application

Make sure you have docker installed, if not check out [Docker](https://www.docker.com/get-started/)

Then install docker compose too

Once everything is to do with docker is set up, run this command.
```commandline
docker compose up --build
```
>Note: The container image especially for fastapi might crush and complain due to missing .env variables. In that case,
> navigate to the core/config.py file and make sure every variable pulling its value from the .env file is created and 
> actually exists in the .env that you are going to create.

Once the container images are built, and they are running, navigate to the following ports on your browser:

* localhost:8050 - fastapi documentation (active endpoints that we're connected with to the frontend.)

* localhost:8025 - Mailpit client for receiving emails.

* localhost:8080 - Adminer interface for our database tables.

* localhost:9000 - Minio interface for our images in object storage.


Additional commands for initialing the database tables using alembic

To initialize alembic
```commandline
docker compose run fastapi-service /bin/sh -c "alembic init alembic"
```

To create migrations
```commandline
docker compose run fastapi-service /bin/sh -c "alembic revision --autogenerate -m'create all tables' "
```

To apply migrations
```commandline
docker compose run fastapi-service /bin/sh -c "alembic upgrade head"
```

To build and run the application
````commandline
docker compose up --build
````