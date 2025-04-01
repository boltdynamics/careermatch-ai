FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies
# RUN apk add --no-cache \
#     gcc \
#     musl-dev \
#     linux-headers \
#     build-base \
#     libffi-dev \
#     poppler-utils \
#     bash

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Make sure the entrypoint script is executable
RUN chmod +x src/app.py

# Create a non-root user to run the app
RUN adduser -D appuser
USER appuser

EXPOSE ${PORT}

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=${PORT}", "--server.address=0.0.0.0"]
