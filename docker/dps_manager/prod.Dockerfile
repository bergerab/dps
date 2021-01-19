# pull official base image
FROM dps_python

# Install netcat for entrypoint.sh
RUN apt-get install -y netcat

# copy project and docker related files
WORKDIR /usr/src/dps_manager
COPY ./dps_manager .

WORKDIR /usr/src/docker/dps_manager/
COPY ./docker/dps_manager .

WORKDIR /usr/src/dps_manager

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# run entrypoint.sh
ENTRYPOINT ["/usr/src/docker/dps_manager/prod.sh"]
