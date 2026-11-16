FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install -e .

CMD ["uvicorn", "transit_advisor.main:app", "--host", "0.0.0.0", "--reload"]
