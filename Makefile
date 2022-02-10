DOCKER=docker
DOCKER = docker
DOCKER_COMPOSE = docker-compose -p console


.PHONY: shared
shared:
	-${DOCKER} network create --subnet=192.168.100.0/24 --ip-range=192.168.100.0/25 --gateway=192.168.100.254 shared


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
	${DOCKER_COMPOSE} run --rm console python3 manage.py migrate --noinput


.PHONY: run
run: shared
	${DOCKER_COMPOSE} up --remove-orphans


.PHONY: tarball
tarball:
	${DOCKER} build . -f docker/tarball/Dockerfile -t tarball
	${DOCKER} run --privileged --rm \
			  -e OUTPUT=/output/var-lib-docker.tgz \
			  -v $(mktemp -d):/var/lib/docker \
			  -v ${PWD}/output:/output tarball


.PHONY: clean
clean:
	${DOCKER_COMPOSE} rm --force


.PHONY: rebuild
rebuild:
ifdef SERVICE
	${DOCKER_COMPOSE} stop ${SERVICE}
	${DOCKER_COMPOSE} rm -f ${SERVICE}
	${DOCKER_COMPOSE} build ${SERVICE}
	${DOCKER_COMPOSE} create ${SERVICE}
	${DOCKER_COMPOSE} start ${SERVICE}
else
	@echo "Please define SERVICE variable, ex:"
	@echo "make rebuild SERVICE=foo"
endif
