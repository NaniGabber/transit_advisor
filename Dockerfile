FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY alembic.ini docker-entrypoint.sh ./
COPY alembic ./alembic

RUN pip install -e .

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

CMD ["uvicorn", "transit_advisor.main:app", "--host", "0.0.0.0", "--reload"]
