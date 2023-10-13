FROM postgres:16-alpine3.18

COPY ./init_db.sql /docker-entrypoint-initdb.d/
