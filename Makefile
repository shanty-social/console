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
