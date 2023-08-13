.POSIX:

export DOCKER_BUILDKIT=1

TAG=ghcr.io/spirkaa/price_ru

PWD=$(shell pwd)

default: run

build:
	@docker build \
		--tag ${TAG} .

test:
	@pytest -v --cov-report html

cleanup:
	@docker rmi -f ${TAG}

run: build
	@docker run \
		--rm \
		--interactive \
		--tty \
		--env-file .env \
		--volume "${PWD}:${PWD}" \
		--workdir "${PWD}" \
		${TAG} \
		python -m price_ru
	@make cleanup --no-print-directory --ignore-errors
