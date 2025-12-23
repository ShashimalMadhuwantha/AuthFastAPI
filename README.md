# SenseGrid IoT Platform - Docker Deployment

Complete IoT platform with real-time device monitoring, MQTT integration, and dual dashboard interfaces.

## 🏗️ Architecture

- **Backend**: FastAPI with TimescaleDB and MQTT integration
- **Frontend**: API-based dashboard with time-series charts
- **Frontend2**: Real-time MQTT dashboard (no database)
- **Simulator**: IoT sensor data simulator
- **Database**: TimescaleDB (PostgreSQL with time-series extensions)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports available: 3000, 3001, 5432, 8000

### Start All Services

```bash
docker-compose up -d
```

### Access the Dashboards

- **API Dashboard**: http://localhost:3000
- **MQTT Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Default Credentials

- Username: `admin`
- Password: `admin123`

## 📦 Services

### 1. Database (TimescaleDB)
- Container: `sensegrid-db`
- Port: `5432`
- Credentials: `postgres/postgres`

### 2. Backend API
- Container: `sensegrid-backend`
- Port: `8000`
- Features:
  - User authentication (JWT)
  - Device management
  - Sensor data storage
  - MQTT integration
  - Time-series queries

### 3. Frontend (API Dashboard)
- Container: `sensegrid-frontend`
- Port: `3000`
- Features:
  - User management
  - Device dashboard
  - Real-time sensor data
  - Time-series charts
  - Customizable time periods (1h - 7 days)

### 4. Frontend2 (MQTT Dashboard)
- Container: `sensegrid-frontend2`
- Port: `3001`
- Features:
  - Direct MQTT connection
  - Real-time data (no database)
  - Configurable data retention
  - Live sensor charts

### 5. Sensor Simulator
- Container: `sensegrid-simulator`
- Features:
  - Simulates 2 devices (LR1, LR2)
  - 4 sensors per device (CT1, CT2, IR, K-Type)
  - MQTT Birth/LWT messages
  - 1-second data publishing

## 🔧 Configuration

### Environment Variables

Edit `.env` or `docker-compose.yml` to configure:

```yaml
# Database
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres
POSTGRES_DB: sensegrid_db

# Backend
SECRET_KEY: your-secret-key
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30

# MQTT
MQTT_BROKER: broker.hivemq.com
MQTT_PORT: 1883
```

## 📊 Data Flow

```
Simulator → MQTT Broker → Backend → Database
                ↓
          Frontend2 (Direct)
                
Backend API → Frontend (via REST)
```

## 🛠️ Development

### Run Individual Services

```bash
# Backend only
docker-compose up backend

# Frontend only
docker-compose up frontend

# Simulator only
docker-compose up simulator
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f simulator
```

### Stop Services

```bash
docker-compose down
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d
```

## 📝 API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/signin` - Login

### Devices
- `GET /api/v1/devices/` - List all devices
- `GET /api/v1/devices/{device_id}` - Get device details
- `GET /api/v1/devices/{device_id}/sensors/{sensor_type}/latest` - Latest reading
- `GET /api/v1/devices/{device_id}/sensors/{sensor_type}/stats` - Statistics
- `GET /api/v1/devices/{device_id}/sensors/{sensor_type}/timeseries` - Time-series data

### Users
- `GET /api/v1/users/` - List users (admin only)
- `POST /api/v1/users/` - Create user (admin only)
- `PUT /api/v1/users/{id}` - Update user (admin only)
- `DELETE /api/v1/users/{id}` - Delete user (admin only)

## 🎯 Features

### Time Period Selection
Both dashboards support customizable time periods:
- **Frontend**: 1h, 6h, 12h, 24h, 48h, 7 days
- **Frontend2**: Data retention (10, 20, 50, 100, 200 points)

### Real-time Updates
- **Frontend**: Auto-refresh every 5 seconds
- **Frontend2**: Live MQTT updates

### Device Status
- Green circle: Online
- Gray circle: Offline
- Last seen timestamp

### Sensor Data
- Current value with unit
- Min/Max statistics
- Time-series charts
- Relative timestamps

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up -d --build
```

### Database connection issues
```bash
docker-compose restart db
docker-compose logs db
```

### MQTT connection issues
- Check if broker.hivemq.com is accessible
- Verify MQTT_BROKER environment variable
- Check simulator logs: `docker-compose logs simulator`

### Frontend not loading
```bash
docker-compose restart frontend frontend2
```

## 📄 License

MIT License

## 👥 Contributors

- Shashimal Madhuwantha

## 🔗 Links

- GitHub: https://github.com/ShashimalMadhuwantha/AuthFastAPI
- MQTT Broker: broker.hivemq.com
