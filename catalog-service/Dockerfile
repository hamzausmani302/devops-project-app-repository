FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
WORKDIR /app
ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 8000

CMD ["python", "main.py"]