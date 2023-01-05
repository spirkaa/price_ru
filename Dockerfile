ARG BUILD_IMAGE=ghcr.io/spirkaa/python:3.11-bullseye-playwright-firefox

FROM ${BUILD_IMAGE}

COPY requirements.txt /

RUN set -eux \
    && pip install --no-cache-dir -r requirements.txt
