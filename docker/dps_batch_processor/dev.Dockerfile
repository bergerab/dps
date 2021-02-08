FROM dps_python

# copy project and docker related files
WORKDIR /usr/src/dps_batch_processor
COPY ./dps_batch_processor .

WORKDIR /usr/src/docker/
COPY ./docker/ .

WORKDIR /usr/src/dps_batch_processor

# install dependencies
RUN pip install --upgrade pip
RUN pip install --editable .

ENTRYPOINT ["/usr/src/docker/dps_batch_processor/dev.sh"]