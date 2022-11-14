FROM python:3.9-slim AS base
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive\
    && apt-get install -y --no-install-recommends\
        iputils-ping=3:20210202-1 \
        telnet=0.17-42 \
        openssh-client=1:8.4p1-5 \
        curl \
        git=1:2.30.2-1 \
        screen=4.8.0-6 \
        nano=5.4-2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m ensurepip && pip3 install --no-cache --upgrade pip setuptools setuptools-scm==6.0.1 wheel

WORKDIR /SDWAN
ARG INDEX_URL
ENV PIP_EXTRA_INDEX_URL=$INDEX_URL
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt ./
COPY ansible/requirements.yml ./ansible/
RUN pip install --no-cache -r requirements.txt && ansible-galaxy install -r ansible/requirements.yml
COPY . .
RUN pip install --no-cache -e .

RUN ./bootstrap
ENV SHELL /bin/bash

EXPOSE 8000
