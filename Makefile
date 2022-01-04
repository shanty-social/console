DOCKER=docker
DOCKER_COMPOSE = docker-compose


.PHONY: build
build:
	${DOCKER_COMPOSE} build


.PHONY: test
test:
	${MAKE} -C back test
	${MAKE} -C front test


.PHONY: lint
lint:
	${MAKE} -C back lint
	${MAKE} -C front lint


.PHONY: ci
ci: test lint


.PHONY: migrate
migrate:
	${DOCKER_COMPOSE} run console python3 manage.py migrate --noinput


.PHONY: run
run:
	${DOCKER_COMPOSE} up


.PHONY: tarball
tarball:
	${DOCKER} build . -f docker/tarball/Dockerfile -t tarball
	${DOCKER} run --privileged --rm \
			  -e OUTPUT=/output/var-lib-docker.tgz \
			  -v $(mktemp -d):/var/lib/docker \
			  -v ${PWD}/output:/output tarball
