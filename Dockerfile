# hadolint global ignore=DL3006

ARG BUILD_IMAGE=ghcr.io/spirkaa/python:3.11-bookworm-playwright-firefox

FROM ${BUILD_IMAGE}

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt
