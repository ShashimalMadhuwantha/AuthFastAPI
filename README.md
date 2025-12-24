# SenseGrid IoT Platform

A complete IoT monitoring platform with real-time sensor data visualization, MQTT integration, and user authentication.

![Platform](https://img.shields.io/badge/Platform-IoT-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start with Docker](#quick-start-with-docker)
- [Developer Setup](#developer-setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

---

## 🌟 Overview

SenseGrid is a full-stack IoT platform for monitoring sensor devices in real-time with:

- **Real-time Data Visualization** - Live charts and dashboards
- **MQTT Integration** - Direct sensor data streaming
- **User Authentication** - JWT-based secure auth
- **Time-Series Database** - TimescaleDB for efficient storage
- **Dual Dashboards** - API-based and MQTT-based monitoring

---

## ✨ Features

### Dashboards

**API Dashboard** (Port 3000)
- Real-time sensor data from REST API
- Configurable refresh intervals (1s - 5min)
- Historical data (1h - 7 days)
- User authentication required

**MQTT Dashboard** (Port 3001)
- Live MQTT data streaming
- Real-time updates (no polling)
- No authentication required

### IoT Features
- Multiple sensor types: CT1, CT2, IR, K-Type
- Device status monitoring
- MQTT birth/death messages
- Configurable topics

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker Desktop (v20.10+)
- Docker Compose (v2.0+)
- 4GB RAM minimum

### Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd Docker
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Start all services**
```bash
docker-compose up -d --build
```

4. **Access the platform**

| Service | URL | Description |
|---------|-----|-------------|
| API Dashboard | http://localhost:3000 | Main dashboard |
| MQTT Dashboard | http://localhost:3001 | Real-time MQTT |
| API Docs | http://localhost:8000/docs | Swagger UI |

5. **Create first user**
- Go to http://localhost:3000
- Click "Sign Up"
- Register and login

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild
docker-compose up -d --build

# Remove everything
docker-compose down -v
```

---

## 💻 Developer Setup

For local development without Docker.

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ or TimescaleDB
- Git

### Backend Setup

1. **Install PostgreSQL and create database**
```bash
psql -U postgres
CREATE DATABASE sensegrid_db;
CREATE USER sensegrid WITH PASSWORD 'sensegrid123';
GRANT ALL PRIVILEGES ON DATABASE sensegrid_db TO sensegrid;
\q
```

2. **Setup Python environment**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run backend**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Open new terminal
cd frontend

# Serve with Python
python -m http.server 3000

# Or with Node.js
npm install -g http-server
http-server -p 3000
```

### Simulator Setup

```bash
# Open new terminal
cd Docker

# Activate backend venv
# Windows:
backend\venv\Scripts\activate
# Linux/Mac:
source backend/venv/bin/activate

# Run simulator
python sensor_simulator.py
```

### Python Dependencies

```txt
# Web Framework
fastapi==0.104.1              # API framework
uvicorn[standard]==0.24.0     # ASGI server

# Database
sqlalchemy==2.0.23            # ORM
psycopg2-binary==2.9.9        # PostgreSQL adapter

# Authentication
python-jose[cryptography]==3.3.0  # JWT tokens
passlib[bcrypt]==1.7.4        # Password hashing

# MQTT
paho-mqtt==1.6.1              # MQTT client

# Validation
pydantic==2.5.0               # Data validation

# Utilities
python-dotenv==1.0.0          # Environment variables
python-multipart==0.0.6       # Form data
requests==2.31.0              # HTTP client
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sensegrid_db
DATABASE_PORT=5432

# Backend
BACKEND_PORT=8000
DATABASE_URL=postgresql://postgres:postgres@db:5432/sensegrid_db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=sensegrid

# Frontend
FRONTEND_PORT=3000
FRONTEND2_PORT=3001
```

### Changing Configuration

1. Edit `.env` file
2. Restart services: `docker-compose down && docker-compose up -d`

---

## 📚 API Documentation

### Authentication

**Register**
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "password123"
}
```

**Login**
```http
POST /api/v1/auth/signin
Content-Type: application/json

{
  "username": "john",
  "password": "password123"
}
```

### Devices

**Get All Devices**
```http
GET /api/v1/devices/
Authorization: Bearer <token>
```

**Get Sensor Data**
```http
GET /api/v1/devices/{device_id}/sensors/{sensor_type}/timeseries?hours=24
Authorization: Bearer <token>
```

**Interactive Docs:** http://localhost:8000/docs

---

## 📁 Project Structure

```
Docker/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API routes
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # API Dashboard
│   ├── css/
│   ├── js/
│   ├── index.html             # Login page
│   ├── devices-dashboard.html # Main dashboard
│   └── Dockerfile
│
├── frontend2/                  # MQTT Dashboard
│   ├── css/
│   ├── js/
│   ├── index.html
│   └── Dockerfile
│
├── sensor_simulator.py         # IoT simulator
├── Dockerfile.simulator
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🐳 Docker Details

### Image Sizes

| Service | Size | Base Image |
|---------|------|------------|
| Backend | 192MB | python:3.11-alpine |
| Simulator | 84.6MB | python:3.11-alpine |
| Frontend | 74.6MB | nginx:1.25-alpine |
| Frontend2 | 74.3MB | nginx:1.25-alpine |
| **Total** | **426MB** | - |

### Multi-Stage Builds

All images use multi-stage builds for optimization:
- **Builder stage**: Compiles dependencies
- **Runtime stage**: Only includes necessary files
- **Result**: 45% smaller than Debian-based images

### Build Commands

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache

# View image sizes
docker images docker-*
```

---

## 🔧 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs -f

# Restart all
docker-compose down
docker-compose up -d --build
```

### Backend Unhealthy

```bash
# Check backend logs
docker-compose logs backend

# Wait for database
# Backend needs 30-40 seconds to start
```

### Frontend Not Loading

- Hard refresh: `Ctrl + Shift + R`
- Or use incognito mode

### No Sensor Data

```bash
# Restart simulator
docker-compose restart simulator

# Check logs
docker-compose logs simulator
```

### Port Conflicts

```bash
# Change ports in .env
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

---

## 🔒 Security Notes

**⚠️ For Production:**

1. Change default passwords in `.env`
2. Generate new `SECRET_KEY`
3. Use HTTPS
4. Restrict database access
5. Configure CORS properly
6. Use environment-specific configs

---

## 📝 License

This project is provided as-is for educational purposes.

---

**Version:** 1.0.0  
**Last Updated:** December 2024
