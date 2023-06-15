# Create from official mysql image
FROM mysql:5.7

RUN echo "USE mysql;" > /docker-entrypoint-initdb.d/timezones.sql &&  mysql_tzinfo_to_sql /usr/share/zoneinfo >> /docker-entrypoint-initdb.d/timezones.sql

# Add a database
ENV MYSQL_DATABASE ${DB_NAME}

# Initial db scripts
COPY ./init-scripts /docker-entrypoint-initdb.d/