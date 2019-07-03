init:
	pip install pip -U
	curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
	poetry self:update
	poetry install
	poetry run pre-commit install


clean:
	rm -rf dist
	rm -rf pip-wheel-metadata
	rm -rf docs
	rm -rf .pytest_cache


test:
	poetry run python -m pytest


lint:
	poetry run pylint -E pydent


docs:
	echo "No documentation"


format:
	poetry run upver
	poetry run black benchlingapi tests


lock:
	poetry run upver
	poetry update


build:
	poetry run upver
	poetry build


release:
	sh scripts/release.sh


klocs:
	find . -name '*.py' | xargs wc -l
