FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/model-cache

COPY requirements.txt .
RUN python -m pip install --no-cache-dir torch==2.8.0 \
        --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip check

COPY app/ ./app/
COPY scripts/ ./scripts/

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]