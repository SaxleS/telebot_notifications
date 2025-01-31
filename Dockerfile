
FROM python:3.11


WORKDIR /app


RUN pip install poetry


COPY pyproject.toml poetry.lock ./
COPY README.md . 
COPY app/ app/
COPY scripts/ scripts/
COPY .env .env


RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi


ENV $(cat .env | xargs)


CMD ["poetry", "run", "python", "scripts/start_bot.py"]