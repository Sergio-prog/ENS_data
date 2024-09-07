PORT = 8000

test:
	poetry run pytest

black:
	poetry run python -m black .

isort:
	poetry run python -m isort --gitignore .

install:
	poetry install

dev:
	poetry run python manage.py runserver $(PORT)

all: install
lint: black isort