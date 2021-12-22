DOCKER_COMPOSE = docker-compose


.PHONY: build
build:
	${DOCKER_COMPOSE} build


.PHONY: test
test:
	${DOCKER_COMPOSE} run console python3 manage.py test --noinput


.PHONY: migrate
migrate:
	${DOCKER_COMPOSE} run console python3 manage.py migrate --noinput


.PHONY: run
run:
	${DOCKER_COMPOSE} up
