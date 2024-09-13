FROM python:3.10.11
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN pip install --upgrade pip setuptools wheel
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

ENV PYTHONUNBUFFERED 1

COPY . .

ENV PORT=8000

EXPOSE $PORT

CMD ["python", "manage.py", "migrate", "--noinput"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]
