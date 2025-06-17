#!/usr/bin/env python3
"""
Kafka Topic Management Script
Creates necessary topics for the air quality monitoring system
"""

import subprocess
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_kafka_topics():
    """Create Kafka topics for air quality data"""
    topics = ["air-quality-paris", "pm25-topic", "no2-topic", "o3-topic", "pm10-topic"]

    kafka_server = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

    for topic in topics:
        try:
            # Check if topic exists
            check_cmd = [
                "kafka-topics.sh",
                "--bootstrap-server",
                kafka_server,
                "--list",
            ]

            result = subprocess.run(
                check_cmd, capture_output=True, text=True, timeout=30
            )

            if topic not in result.stdout:
                # Create topic
                create_cmd = [
                    "kafka-topics.sh",
                    "--bootstrap-server",
                    kafka_server,
                    "--create",
                    "--topic",
                    topic,
                    "--partitions",
                    "3",
                    "--replication-factor",
                    "1",
                ]

                subprocess.run(create_cmd, check=True, timeout=30)
                logger.info(f"Created Kafka topic: {topic}")
            else:
                logger.info(f"Kafka topic already exists: {topic}")

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout creating topic: {topic}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating topic {topic}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating topic {topic}: {e}")


if __name__ == "__main__":
    # Wait for Kafka to be ready
    logger.info("Waiting for Kafka to be ready...")
    time.sleep(30)

    # Create topics
    create_kafka_topics()

    logger.info("Topic creation completed")
