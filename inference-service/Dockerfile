FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app


CMD ["python", "main.py"]