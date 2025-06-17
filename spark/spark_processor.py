#!/usr/bin/env python3
"""
Spark Streaming Application for Air Quality Data Processing
Consumes data from Kafka and stores processed data in InfluxDB
"""

import json
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
)
import requests
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AirQualityProcessor:
    def __init__(self):
        self.kafka_servers = "kafka:9092"
        self.kafka_topic = "air-quality-paris"
        self.influxdb_url = "http://influxdb:8086"
        self.influxdb_database = "air_quality"

        # Initialize Spark session
        self.spark = self.create_spark_session()

        # Define schema for air quality data
        self.air_quality_schema = StructType(
            [
                StructField("timestamp", StringType(), True),
                StructField("location", StringType(), True),
                StructField(
                    "coordinates",
                    StructType(
                        [
                            StructField("lat", DoubleType(), True),
                            StructField("lon", DoubleType(), True),
                        ]
                    ),
                    True,
                ),
                StructField("aqi", IntegerType(), True),
                StructField(
                    "components",
                    StructType(
                        [
                            StructField("co", DoubleType(), True),
                            StructField("no", DoubleType(), True),
                            StructField("no2", DoubleType(), True),
                            StructField("o3", DoubleType(), True),
                            StructField("so2", DoubleType(), True),
                            StructField("pm2_5", DoubleType(), True),
                            StructField("pm10", DoubleType(), True),
                            StructField("nh3", DoubleType(), True),
                        ]
                    ),
                    True,
                ),
            ]
        )

    def create_spark_session(self):
        """Create Spark session with Kafka support"""
        return (
            SparkSession.builder.appName("AirQualityProcessor")
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint")
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
            .getOrCreate()
        )

    def create_influxdb_database(self):
        """Create InfluxDB database if it doesn't exist"""
        max_retries = 10
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.post(
                    f"{self.influxdb_url}/query",
                    params={"q": f"CREATE DATABASE {self.influxdb_database}"},
                    timeout=10,
                )
                if response.status_code == 200:
                    logger.info(
                        f"InfluxDB database '{self.influxdb_database}' created/verified"
                    )
                    return True
                else:
                    logger.warning(f"InfluxDB response: {response.status_code}")
            except Exception as e:
                retry_count += 1
                logger.error(
                    f"Failed to create InfluxDB database (attempt {retry_count}/{max_retries}): {e}"
                )
                time.sleep(5)

        logger.error("Failed to create InfluxDB database after maximum retries")
        return False

    def write_to_influxdb(self, df, epoch_id):
        """Write DataFrame to InfluxDB"""
        try:
            # Convert DataFrame to list of dictionaries
            rows = df.collect()

            if not rows:
                logger.info(f"No data to write in batch {epoch_id}")
                return

            # Prepare InfluxDB line protocol data
            lines = []
            for row in rows:
                # Convert timestamp to nanoseconds
                timestamp_str = row.timestamp
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                timestamp_ns = int(dt.timestamp() * 1_000_000_000)

                # Create line protocol format
                tags = f"location={row.location},lat={row.coordinates_lat},lon={row.coordinates_lon}"
                fields = [
                    f"aqi={row.aqi}i",
                    f"co={row.components_co}",
                    f"no={row.components_no}",
                    f"no2={row.components_no2}",
                    f"o3={row.components_o3}",
                    f"so2={row.components_so2}",
                    f"pm2_5={row.components_pm2_5}",
                    f"pm10={row.components_pm10}",
                    f"nh3={row.components_nh3}",
                ]

                line = f"air_quality,{tags} {','.join(fields)} {timestamp_ns}"
                lines.append(line)

            # Write to InfluxDB
            data = "\n".join(lines)
            response = requests.post(
                f"{self.influxdb_url}/write",
                params={"db": self.influxdb_database},
                data=data,
                headers={"Content-Type": "text/plain"},
                timeout=30,
            )

            if response.status_code == 204:
                logger.info(
                    f"Successfully wrote {len(rows)} records to InfluxDB (batch {epoch_id})"
                )
            else:
                logger.error(
                    f"Failed to write to InfluxDB: {response.status_code} - {response.text}"
                )

        except Exception as e:
            logger.error(f"Error writing to InfluxDB (batch {epoch_id}): {e}")

    def process_air_quality_data(self, df):
        """Process and flatten air quality data"""
        return df.select(
            col("timestamp"),
            col("location"),
            col("coordinates.lat").alias("coordinates_lat"),
            col("coordinates.lon").alias("coordinates_lon"),
            col("aqi"),
            col("components.co").alias("components_co"),
            col("components.no").alias("components_no"),
            col("components.no2").alias("components_no2"),
            col("components.o3").alias("components_o3"),
            col("components.so2").alias("components_so2"),
            col("components.pm2_5").alias("components_pm2_5"),
            col("components.pm10").alias("components_pm10"),
            col("components.nh3").alias("components_nh3"),
        )

    def run(self):
        """Main processing loop"""
        logger.info("Starting Air Quality Spark Processor...")

        # Create InfluxDB database
        if not self.create_influxdb_database():
            logger.error("Failed to initialize InfluxDB, continuing anyway...")

        try:
            # Read from Kafka
            kafka_df = (
                self.spark.readStream.format("kafka")
                .option("kafka.bootstrap.servers", self.kafka_servers)
                .option("subscribe", self.kafka_topic)
                .option("startingOffsets", "latest")
                .option("failOnDataLoss", "false")
                .load()
            )

            # Parse JSON data
            parsed_df = kafka_df.select(
                from_json(col("value").cast("string"), self.air_quality_schema).alias(
                    "data"
                )
            ).select("data.*")

            # Process the data
            processed_df = self.process_air_quality_data(parsed_df)

            # Write to InfluxDB using foreachBatch
            query = (
                processed_df.writeStream.foreachBatch(self.write_to_influxdb)
                .outputMode("append")
                .trigger(processingTime="30 seconds")
                .start()
            )

            logger.info("Spark streaming query started")
            query.awaitTermination()

        except Exception as e:
            logger.error(f"Error in Spark processing: {e}")
            raise
        finally:
            self.spark.stop()


if __name__ == "__main__":
    processor = AirQualityProcessor()
    processor.run()
