FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=8080
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 8081
EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "main.py"]