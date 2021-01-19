FROM dps_python

# Install netcat for entrypoint.sh
RUN apt-get install -y netcat

COPY ./dps_database_manager /usr/src/dps_database_manager

WORKDIR /usr/src/docker/dps_database_manager/
COPY ./docker/dps_database_manager .

WORKDIR /usr/src/dps_database_manager

# install dependencies
RUN pip install --upgrade pip
RUN pip install .

ENTRYPOINT ["/usr/src/docker/dps_database_manager/dev.sh"]