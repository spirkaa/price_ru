ARG PYTHON_IMAGE=ghcr.io/spirkaa/python:3.10-bullseye-playwright-firefox

FROM ${PYTHON_IMAGE}

COPY requirements.txt /

RUN set -eux \
    && pip install --no-cache-dir -r requirements.txt
