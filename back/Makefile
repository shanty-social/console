.venv: Pipfile
	PIPENV_VENV_IN_PROJECT=true pipenv install --dev
	touch .venv


.PHONY: deps
deps: .venv


.PHONY: test
test: deps
	pipenv run pytest --cov=api tests/
	pipenv run coverage report -m


.PHONY: lint
lint: deps
	pipenv run flake8 api/
