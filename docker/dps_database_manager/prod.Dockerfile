FROM dps_python

# Install netcat for entrypoint.sh
RUN apt-get install -y netcat

# copy project and docker related files
WORKDIR /usr/src/dps_database_manager
COPY ./dps_database_manager .

WORKDIR /usr/src/docker/
COPY ./docker/ .

WORKDIR /usr/src/dps_database_manager

# install dependencies
RUN pip install --upgrade pip
RUN pip install .

WORKDIR /usr/src/dps_database_manager/dps_database_manager

ENTRYPOINT ["/usr/src/docker/dps_database_manager/prod.sh"]