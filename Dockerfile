FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir uv
RUN uv sync

COPY app.py .
COPY send_mail.py .
COPY __init__.py

EXPOSE 8002

CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
