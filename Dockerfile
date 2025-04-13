FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN chmod +x app.py

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE ${PORT}

ENTRYPOINT streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0
