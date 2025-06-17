# Air Quality Monitoring System for Paris

This project implements a real-time air quality monitoring system for Paris using modern data streaming technologies.

## Architecture

The system consists of the following components:

- **Kafka**: Message broker for streaming air quality data
- **Producer**: Python service that fetches air quality data and publishes to Kafka
- **Spark**: Stream processing engine for real-time data processing
- **InfluxDB**: Time-series database for storing processed data
- **Grafana**: Visualization dashboard for monitoring air quality trends

## Features

- Real-time air quality data ingestion
- Processing of multiple pollutants: PM2.5, PM10, NO2, O3, CO, SO2, NH3
- Air Quality Index (AQI) monitoring
- Anomaly detection for pollution spikes
- Interactive Grafana dashboards
- Time-series data storage

## Prerequisites

- Docker and Docker Compose
- OpenWeatherMap API key (required for real air quality data)

## Quick Start

1. **Clone the repository** (if not already done)

2. **Set up environment variables** (optional):
   ```bash
   export OPENWEATHER_API_KEY=your_api_key_here
   ```

3. **Build and start the services**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
   
   The system will automatically:
   - Start Zookeeper and Kafka
   - Create necessary Kafka topics
   - Start the producer and Spark processor
   - Initialize InfluxDB with the air quality database
   - Set up Grafana with pre-configured dashboards

4. **Monitor the startup process**:
   ```bash
   # Check if all services are running
   docker-compose ps
   
   # View logs to ensure everything is working
   docker-compose logs -f
   ```

5. **Access Grafana dashboard**:
   - URL: http://localhost:3000
   - Default credentials: admin/admin
   - Dashboard: "Paris Air Quality Monitoring"

## System Components

### Kafka Topic Setup
- Automatic topic creation on startup
- Topics: `air-quality-paris`, `pm25-topic`, `no2-topic`, `o3-topic`, `pm10-topic`
- Configuration: 3 partitions, replication factor 1

### Producer Service
- Fetches air quality data from OpenWeatherMap API
- Publishes data to Kafka topic every 3 minutes
- Stops if API is unavailable (requires valid API key)
- Located in `./producer/`

### Spark Processing Service
- Consumes data from Kafka
- Processes and transforms air quality data
- Detects anomalies and pollution spikes
- Stores processed data in InfluxDB
- Located in `./spark/`

### InfluxDB
- Time-series database for air quality metrics
- Database: `air_quality`
- Accessible on port 8086

### Grafana
- Visualization dashboard
- Pre-configured with InfluxDB datasource
- Dashboard shows AQI, PM2.5, PM10, NO2, O3 trends
- Accessible on port 3000

## Data Schema

The system processes the following air quality metrics:

```json
{
  "timestamp": "2025-06-17T10:30:00Z",
  "location": "Paris",
  "coordinates": {"lat": 48.8566, "lon": 2.3522},
  "aqi": 2,
  "components": {
    "co": 233.4,
    "no": 0.12,
    "no2": 19.3,
    "o3": 89.2,
    "so2": 8.1,
    "pm2_5": 12.5,
    "pm10": 18.7,
    "nh3": 2.1
  }
}
```

## Testing the System

### 1. Verify all services are running:
```bash
docker-compose ps
```
All services should show "Up" status.

### 2. Check Kafka topics were created:
```bash
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```
You should see the following topics:
- air-quality-paris
- pm25-topic
- no2-topic
- o3-topic
- pm10-topic

### 3. Monitor data flow:

**Check producer is sending data:**
```bash
docker-compose logs -f producer
```
You should see logs about fetching and publishing air quality data.

**Check Spark is processing data:**
```bash
docker-compose logs -f spark
```
Look for successful data processing and InfluxDB writes.

**Verify data in InfluxDB:**
```bash
curl "http://localhost:8086/query?q=SELECT * FROM air_quality ORDER BY time DESC LIMIT 10&db=air_quality"
```

### 4. Test Grafana Dashboard:
1. Open http://localhost:3000
2. Login with admin/admin
3. Navigate to the "Paris Air Quality Monitoring" dashboard
4. Verify charts are displaying data (may take a few minutes for initial data)

### 5. Load Testing:
Monitor resource usage during operation:
```bash
docker stats
```

## Monitoring and Troubleshooting

### View service logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f producer
docker-compose logs -f spark
```

### Check service status:
```bash
docker-compose ps
```

### Restart services:
```bash
docker-compose restart
```

### Access InfluxDB directly:
```bash
curl "http://localhost:8086/query?q=SELECT * FROM air_quality LIMIT 10&db=air_quality"
```

## Development

### Adding new pollutant monitoring:
1. Update the producer to include new metrics
2. Modify the Spark processor schema
3. Add new visualizations to Grafana dashboard

### Customizing data sources:
1. Modify `producer/producer.py` to integrate with other APIs
2. Update the data schema in `spark/spark_processor.py`

## API Key Setup

To use real air quality data from OpenWeatherMap:

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Set the environment variable:
   ```bash
   export OPENWEATHER_API_KEY=your_actual_api_key
   ```
4. Restart the producer service:
   ```bash
   docker-compose restart producer
   ```

## Stopping the System

```bash
docker-compose down
```

To remove all data volumes:
```bash
docker-compose down -v
```

## Project Structure

```
├── docker-compose.yml          # Main orchestration file
├── kafka-setup.py             # Kafka topic management script
├── producer/                   # Data producer service
│   ├── Dockerfile
│   ├── producer.py
│   └── requirements.txt
├── spark/                      # Stream processing service
│   ├── Dockerfile
│   ├── spark_processor.py
│   └── requirements.txt
├── grafana/                    # Grafana configuration
│   └── provisioning/
│       ├── datasources/        # InfluxDB datasource config
│       └── dashboards/         # Pre-built air quality dashboard
├── docs/
│   └── README.md              # Additional documentation
├── LICENSE
└── README.md                  # This file
```

## Troubleshooting

### Common Issues:

1. **Services not starting**: Check logs and ensure ports are available
2. **No data in Grafana**: Verify producer is sending data and Spark is processing
3. **API key issues**: Ensure you have a valid OpenWeatherMap API key
4. **Memory issues**: Adjust Docker resource limits if needed

### Health Checks:

```bash
# Check Kafka topics
docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check InfluxDB data
curl "http://localhost:8086/query?q=SHOW+DATABASES"
```
