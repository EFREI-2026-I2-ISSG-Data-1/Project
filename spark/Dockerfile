# Air Quality Spark Processor
FROM bitnami/spark:3.5

# Switch to root to install packages
USER root

# Install apt packages including curl for downloading JARs
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Kafka connector for Spark 3.5 with Scala 2.12
RUN curl -L -o /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.5.6.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.6/spark-sql-kafka-0-10_2.12-3.5.6.jar && \
    curl -L -o /opt/bitnami/spark/jars/kafka-clients-3.4.1.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar && \
    curl -L -o /opt/bitnami/spark/jars/commons-pool2-2.11.1.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar && \
    curl -L -o /opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.6.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.6/spark-token-provider-kafka-0-10_2.12-3.5.6.jar

# Install Python packages
COPY requirements.txt /opt/spark-app/
RUN pip install --no-cache-dir -r /opt/spark-app/requirements.txt

# Copy Spark application
COPY spark_processor.py /opt/spark-app/

# Set working directory
WORKDIR /opt/spark-app

# Create directories with proper permissions for spark user (1001)
RUN mkdir -p /tmp/checkpoint && chown -R 1001:1001 /tmp/checkpoint && chmod 755 /tmp/checkpoint
RUN mkdir -p /tmp/spark-temp && chown -R 1001:1001 /tmp/spark-temp && chmod 755 /tmp/spark-temp
RUN mkdir -p /opt/spark-app && chown -R 1001:1001 /opt/spark-app && chmod 755 /opt/spark-app

# Switch back to spark user
USER 1001

# Set environment variables to avoid artifacts issues
ENV SPARK_LOCAL_DIRS=/tmp/spark-temp
ENV SPARK_WORKER_DIR=/tmp/spark-temp

# Run the Spark application
CMD ["python", "/opt/spark-app/spark_processor.py"]
