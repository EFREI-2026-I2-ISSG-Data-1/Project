# Air Quality Producer for Paris
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy producer application
COPY producer.py /app/

# Environment variables
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=air-quality-paris
ENV OPENWEATHER_API_KEY=demo_key

# Make producer script executable
RUN chmod +x producer.py

# Run the producer
CMD ["python", "producer.py"]
