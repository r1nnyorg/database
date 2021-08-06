FROM postgres:alpine
ENV POSTGRES_PASSWORD postgres
COPY *.sql /docker-entrypoint-initdb.d/
