FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir uv
RUN uv sync

COPY app.py .

EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
