.POSIX:

export DOCKER_BUILDKIT=1

default: run

TAG=price_ru
PWD=$(shell pwd)

build:
	@docker build \
		--tag ${TAG} .

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
