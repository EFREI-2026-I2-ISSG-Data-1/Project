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
            "OPENWEATHER_API_KEY", "1db3aed366121b0039d8f0b8ad1f0833"
        )
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
                # Fetch real data from API only
                data = self.fetch_air_quality_data()

                # If real data fails, stop the producer
                if data is None:
                    logger.error(
                        "Failed to fetch data from OpenWeather API. Producer will stop."
                    )
                    logger.error("Please check your API key and internet connection.")
                    break

                # Send to Kafka
                if self.send_to_kafka(data):
                    logger.info(
                        f"Sent real air quality data: AQI={data['aqi']}, PM2.5={data['components'].get('pm2_5', 'N/A')}"
                    )
                else:
                    logger.error("Failed to send data to Kafka. Producer will stop.")
                    break

                # Wait before next reading (every 3 minutes)
                time.sleep(180)

            except KeyboardInterrupt:
                logger.info("Producer stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in producer loop: {e}")
                logger.error("Producer will stop due to error.")
                break

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
