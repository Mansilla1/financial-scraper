FROM postgres:11.2-alpine

ENV POSTGRES_DB financial
ENV POSTGRES_USER financial
ENV POSTGRES_PASSWORD financial

COPY ./scripts/db/financial.sql /docker-entrypoint-initdb.d

EXPOSE 5432
