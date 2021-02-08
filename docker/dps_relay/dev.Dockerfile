FROM dps_python

# copy project and docker related files
WORKDIR /usr/src/dps_relay
COPY ./dps_relay .

WORKDIR /usr/src/docker/
COPY ./docker/ .

WORKDIR /usr/src/dps_relay

# install dependencies
RUN pip install --upgrade pip
RUN pip install --editable .

WORKDIR /usr/src/dps_relay/dps_relay