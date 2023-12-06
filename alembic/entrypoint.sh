while ! psql postgresql://postgres:password@database:5432; do echo "Waiting for db to initialize"; sleep 3; done

alembic upgrade head
