FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Local Compose uses 8000. Render sets $PORT (usually 10000).
EXPOSE 8000 10000

# Wait for Postgres, run alembic upgrade head, then start uvicorn.
CMD ["python", "entrypoint.py"]
