# Air Quality Spark Processor
FROM bitnami/spark:latest

# Switch to root to install packages
USER root

# Install Python packages
COPY requirements.txt /opt/spark-app/
RUN pip install --no-cache-dir -r /opt/spark-app/requirements.txt

# Copy Spark application
COPY spark_processor.py /opt/spark-app/

# Set working directory
WORKDIR /opt/spark-app

# Create checkpoint directory and artifacts directory with proper permissions
RUN mkdir -p /tmp/checkpoint && chmod 777 /tmp/checkpoint
RUN mkdir -p /opt/spark-app/artifacts && chmod 777 /opt/spark-app/artifacts
RUN chmod -R 777 /opt/spark-app

# Switch back to spark user
USER 1001

# Run the Spark application
CMD ["python", "/opt/spark-app/spark_processor.py"]
