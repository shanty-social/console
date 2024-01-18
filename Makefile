DOCKER=docker
DOCKER = docker
DOCKER_COMPOSE = docker-compose -p console


.PHONY: build
build:
	docker buildx build -t console/console --load -f docker/console/Dockerfile .
	docker buildx build -t console/net --load -f docker/net/Dockerfile .
	docker buildx build -t console/conduit --load -f docker/conduit/Dockerfile .


.PHONY: run
run:
	${DOCKER_COMPOSE} up


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
