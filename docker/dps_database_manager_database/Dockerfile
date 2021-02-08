FROM timescale/timescaledb:latest-pg11

WORKDIR /docker-entrypoint-initdb.d
ADD ./dps_database_manager/schema.sql /docker-entrypoint-initdb.d/003_dps_manager_database_schema.sql

EXPOSE 5432