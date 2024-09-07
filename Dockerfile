FROM python:3.11.9

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . .

ENV PORT=8000

EXPOSE $PORT

CMD ["python", "manage.py", "migrate", "--noinput"]
CMD python manage.py runserver $PORT
