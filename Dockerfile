ARG PYTHON_IMAGE=python:3.10-slim-bullseye

FROM ${PYTHON_IMAGE}

COPY requirements.txt .

RUN set -eux \
    && pip install --no-cache-dir -r requirements.txt
