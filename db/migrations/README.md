## Running Database Migrations

## Initialize Database

```sh
docker exec -it ai-api-container zsh

alembic -c db/alembic.ini revision --autogenerate -m "Initialize DB"
alembic -c db/alembic.ini upgrade head
```

## How the migrations folder was created

```sh
docker exec -it ai-api-container zsh

cd db
alembic init migration
```

## References:

- [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/)
