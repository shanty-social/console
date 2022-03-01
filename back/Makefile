VENV=$(shell pipenv --venv)


${VENV}: Pipfile
	pipenv install --dev
	touch ${VENV}


.PHONY: deps
deps: ${VENV}


.PHONY: test
test: deps
	pipenv run pytest --cov=api tests/
	pipenv run coverage report -m


.PHONY: lint
lint: deps
	pipenv run flake8 api/
