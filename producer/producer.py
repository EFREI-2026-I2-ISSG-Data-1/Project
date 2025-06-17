#!/usr/bin/env python3
"""
Air Quality Data Producer for Paris
Fetches data from OpenWeatherMap API and publishes to Kafka
"""

import json
import time
import requests
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AirQualityProducer:
    def __init__(self):
        self.kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.topic = os.getenv("KAFKA_TOPIC", "air-quality-paris")
        self.api_key = os.getenv(
            "OPENWEATHER_API_KEY", "demo_key"
        )  # Replace with real API key
        self.api_url = "http://api.openweathermap.org/data/2.5/air_pollution"

        # Paris coordinates
        self.lat = 48.8566
        self.lon = 2.3522

        # Initialize Kafka producer
        self.producer = None
        self.init_kafka_producer()

    def init_kafka_producer(self):
        """Initialize Kafka producer with retry logic"""
        max_retries = 10
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=[self.kafka_servers],
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    api_version=(0, 10, 1),
                    retries=5,
                    request_timeout_ms=30000,
                )
                logger.info(f"Kafka producer initialized successfully")
                return
            except Exception as e:
                retry_count += 1
                logger.error(
                    f"Failed to initialize Kafka producer (attempt {retry_count}/{max_retries}): {e}"
                )
                time.sleep(5)

        raise Exception("Failed to initialize Kafka producer after maximum retries")

    def fetch_air_quality_data(self):
        """Fetch air quality data from OpenWeatherMap API"""
        try:
            params = {"lat": self.lat, "lon": self.lon, "appid": self.api_key}

            response = requests.get(self.api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract relevant data
                air_quality_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "location": "Paris",
                    "coordinates": {"lat": self.lat, "lon": self.lon},
                    "aqi": data["list"][0]["main"]["aqi"],  # Air Quality Index
                    "components": data["list"][0][
                        "components"
                    ],  # CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3
                }

                return air_quality_data
            else:
                logger.error(
                    f"API request failed with status code: {response.status_code}"
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching air quality data: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            return None

    def generate_mock_data(self):
        """Generate mock air quality data when API is not available"""
        import random

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "location": "Paris",
            "coordinates": {"lat": self.lat, "lon": self.lon},
            "aqi": random.randint(1, 5),  # Air Quality Index (1-5)
            "components": {
                "co": round(random.uniform(200, 400), 2),  # Carbon monoxide (μg/m³)
                "no": round(random.uniform(0, 50), 2),  # Nitric oxide (μg/m³)
                "no2": round(random.uniform(10, 80), 2),  # Nitrogen dioxide (μg/m³)
                "o3": round(random.uniform(50, 150), 2),  # Ozone (μg/m³)
                "so2": round(random.uniform(5, 30), 2),  # Sulphur dioxide (μg/m³)
                "pm2_5": round(
                    random.uniform(5, 50), 2
                ),  # Fine particles matter (μg/m³)
                "pm10": round(
                    random.uniform(10, 80), 2
                ),  # Coarse particulate matter (μg/m³)
                "nh3": round(random.uniform(1, 20), 2),  # Ammonia (μg/m³)
            },
        }

    def send_to_kafka(self, data):
        """Send data to Kafka topic"""
        try:
            future = self.producer.send(self.topic, value=data)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Message sent to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False

    def run(self):
        """Main producer loop"""
        logger.info("Starting Air Quality Producer for Paris...")
        logger.info(
            f"Using API key: {'***' if self.api_key != 'demo_key' else 'demo_key'}"
        )

        while True:
            try:
                # Try to fetch real data first
                data = self.fetch_air_quality_data()

                # If real data fails, use mock data
                if data is None:
                    logger.warning("Using mock data due to API unavailability")
                    data = self.generate_mock_data()

                # Send to Kafka
                if self.send_to_kafka(data):
                    logger.info(
                        f"Sent air quality data: AQI={data['aqi']}, PM2.5={data['components'].get('pm2_5', 'N/A')}"
                    )

                # Wait before next reading (every 5 minutes)
                time.sleep(300)

            except KeyboardInterrupt:
                logger.info("Producer stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in producer loop: {e}")
                time.sleep(30)  # Wait before retrying

    def close(self):
        """Clean up resources"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


if __name__ == "__main__":
    producer = AirQualityProducer()
    try:
        producer.run()
    finally:
        producer.close()
