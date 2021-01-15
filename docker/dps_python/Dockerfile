# pull official base image
FROM python:3.8-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y python3-psycopg2

# install dependencies
RUN pip install --upgrade pip
COPY ./dps_manager/requirements.txt .
RUN pip install -r requirements.txt

# install dplib
WORKDIR /usr/src/dplib
COPY ./dplib/ .
RUN pip install .

# install dps_services
WORKDIR /usr/src/dps_services
COPY ./dps_services/ .
RUN pip install .

# install dps_client
WORKDIR /usr/src/dps_client
COPY ./dps_client/ .
RUN pip install .
