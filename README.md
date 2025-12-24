# SenseGrid IoT Platform

A complete IoT monitoring platform with real-time sensor data visualization, MQTT integration, and user authentication.

![Platform](https://img.shields.io/badge/Platform-IoT-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-PostgreSQL-336791?logo=postgresql)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start)
- [Development Setup](#development-setup)
  - [Local Development (Without Docker)](#local-development-without-docker)
  - [Docker Build Process](#docker-build-process)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)


---

## 🌟 Overview

SenseGrid is a full-stack IoT platform designed for monitoring and managing sensor devices in real-time. It provides:

- **Real-time Data Visualization**: Live charts and dashboards
- **MQTT Integration**: Direct sensor data streaming
- **User Authentication**: Secure JWT-based auth system
- **Time-Series Database**: Efficient storage with TimescaleDB
- **Dual Dashboards**: API-based and MQTT-based monitoring
- **Device Simulation**: Built-in sensor simulator for testing

---

## ✨ Features

### 🔐 Authentication & User Management
- User registration and login
- JWT token-based authentication
- Secure password hashing
- Session management

### 📊 Dashboards

#### 1. **API Dashboard** (Frontend)
- Real-time sensor data from REST API
- Configurable refresh intervals (1s - 5min)
- Historical data visualization (1h - 7 days)
- Device status monitoring
- Interactive charts with Chart.js

#### 2. **MQTT Dashboard** (Frontend2)
- Live MQTT data streaming
- Real-time updates (no polling)
- Time-based data filtering
- Device online/offline status
- Automatic reconnection

### 📡 IoT Features
- Support for multiple sensor types:
  - CT1/CT2 (Current Transformers)
  - IR (Infrared Temperature)
  - K-Type (Thermocouple)
- Device birth/death messages
- Last Will and Testament (LWT)
- Configurable MQTT topics

### 🗄️ Data Management
- TimescaleDB for time-series data
- Automatic data retention
- Efficient querying
- Statistics calculation (min, max, avg)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SenseGrid Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Frontend   │  │  Frontend2   │  │   Backend    │      │
│  │  (Nginx)     │  │  (Nginx)     │  │  (FastAPI)   │      │
│  │  Port 3000   │  │  Port 3001   │  │  Port 8000   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         │    REST API      │                  │               │
│         └──────────────────┴──────────────────┘               │
│                            │                                  │
│                            │                                  │
│                   ┌────────▼────────┐                        │
│                   │   TimescaleDB   │                        │
│                   │   Port 5432     │                        │
│                   └─────────────────┘                        │
│                                                               │
│  ┌──────────────┐         MQTT          ┌──────────────┐   │
│  │  Simulator   │◄──────────────────────►│ HiveMQ Broker│   │
│  │  (Python)    │                        │  (External)  │   │
│  └──────────────┘                        └──────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Docker Desktop** (v20.10 or higher)
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version`

2. **Docker Compose** (v2.0 or higher)
   - Usually included with Docker Desktop
   - Verify: `docker-compose --version`

3. **Git** (optional, for cloning)
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 2GB free space
- **Network**: Internet connection for MQTT broker

---

## 🚀 Quick Start

Follow these steps to get the platform running:

### Step 1: Clone or Download the Project

```bash
# Option A: Clone with Git
git clone <repository-url>
cd Docker

# Option B: Download ZIP and extract
# Then navigate to the extracted folder
```

### Step 2: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# The default values work out of the box!
# No need to edit unless you want custom settings
```

### Step 3: Start All Services

```bash
# Build and start all containers
docker-compose up -d --build
```

This command will:
- Build Docker images (first time: ~5-10 minutes)
- Start database, backend, frontends, and simulator
- Create necessary networks and volumes

### Step 4: Wait for Services to Initialize

```bash
# Check if all services are running
docker-compose ps

# You should see:
# - sensegrid-db (healthy)
# - sensegrid-backend (healthy)
# - sensegrid-frontend (running)
# - sensegrid-frontend2 (running)
# - sensegrid-simulator (running)
```

### Step 5: Access the Platform

Open your browser and navigate to:

| Service | URL | Description |
|---------|-----|-------------|
| **API Dashboard** | http://localhost:3000 | Main dashboard with authentication |
| **MQTT Dashboard** | http://localhost:3001 | Real-time MQTT monitoring |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs (Swagger) |
| **Alternative API Docs** | http://localhost:8000/redoc | ReDoc API documentation |

### Step 6: Create Your First User

1. Go to http://localhost:3000
2. Click **"Sign Up"**
3. Fill in the registration form:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `admin123` (or your choice)
4. Click **"Sign Up"**
5. You'll be redirected to the login page
6. Log in with your credentials

### Step 7: Explore the Dashboards

**API Dashboard** (http://localhost:3000):
- Click on **"Devices"** in the navigation
- You'll see real-time sensor data from LR1 and LR2 devices
- Click the ⚙️ settings icon to:
  - **Realtime tab**: Change refresh interval (1s - 5min)
  - **History tab**: Change time period (1h - 7 days)

**MQTT Dashboard** (http://localhost:3001):
- Opens directly (no login required)
- Shows live MQTT data
- Click ⚙️ to change time period

---

## 💻 Development Setup

This section is for developers who want to modify the code, add features, or run the project locally without Docker.

### Local Development (Without Docker)

#### Prerequisites for Local Development

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **PostgreSQL 15+** or **TimescaleDB**
   - Download PostgreSQL: https://www.postgresql.org/download/
   - Or TimescaleDB: https://docs.timescale.com/install/latest/
   - Verify: `psql --version`

3. **Node.js 18+** (for frontend development tools, optional)
   - Download: https://nodejs.org/
   - Verify: `node --version`

4. **Git**
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Docker
```

#### Step 2: Set Up PostgreSQL Database

```bash
# Start PostgreSQL service
# Windows: Start from Services
# Linux: sudo systemctl start postgresql
# Mac: brew services start postgresql

# Create database
psql -U postgres
CREATE DATABASE sensegrid_db;
CREATE USER sensegrid WITH PASSWORD 'sensegrid123';
GRANT ALL PRIVILEGES ON DATABASE sensegrid_db TO sensegrid;
\q

# Enable TimescaleDB extension (if using TimescaleDB)
psql -U postgres -d sensegrid_db
CREATE EXTENSION IF NOT EXISTS timescaledb;
\q
```

#### Step 3: Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your local database credentials
# DATABASE_URL=postgresql://sensegrid:sensegrid123@localhost:5432/sensegrid_db
```

#### Step 4: Initialize Database Tables

```bash
# Still in backend directory with venv activated
# Run the backend once to create tables
python -m uvicorn main:app --reload

# Or use Alembic migrations (if configured)
# alembic upgrade head
```

#### Step 5: Run Backend

```bash
# In backend directory with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Step 6: Run Sensor Simulator

```bash
# Open a new terminal
cd Docker

# Activate virtual environment (same as backend)
# Windows:
backend\venv\Scripts\activate
# Linux/Mac:
source backend/venv/bin/activate

# Run simulator
python sensor_simulator.py
```

#### Step 7: Serve Frontend (Development)

**Option A: Using Python HTTP Server**

```bash
# Open a new terminal
cd Docker/frontend

# Python 3
python -m http.server 3000

# Frontend available at http://localhost:3000
```

**Option B: Using Node.js HTTP Server**

```bash
# Install http-server globally
npm install -g http-server

# Serve frontend
cd Docker/frontend
http-server -p 3000

# Frontend available at http://localhost:3000
```

**Option C: Using Nginx (Production-like)**

Install Nginx and configure it to serve from `frontend/` directory on port 3000.

#### Step 8: Serve Frontend2 (MQTT Dashboard)

```bash
# Open a new terminal
cd Docker/frontend2

# Serve on port 3001
python -m http.server 3001

# MQTT Dashboard available at http://localhost:3001
```

### Python Dependencies Explained

Here's what each dependency in `backend/requirements.txt` does:

```txt
# Web Framework
fastapi==0.104.1              # Modern, fast web framework for APIs
uvicorn[standard]==0.24.0     # ASGI server to run FastAPI

# Database
sqlalchemy==2.0.23            # ORM for database operations
psycopg2-binary==2.9.9        # PostgreSQL adapter for Python
alembic==1.12.1               # Database migrations (optional)

# Data Validation
pydantic==2.5.0               # Data validation using Python type hints
pydantic-settings==2.1.0      # Settings management

# Authentication
python-jose[cryptography]==3.3.0  # JWT token creation/validation
passlib[bcrypt]==1.7.4        # Password hashing
python-multipart==0.0.6       # Form data parsing

# MQTT
paho-mqtt==1.6.1              # MQTT client library

# Utilities
python-dotenv==1.0.0          # Load environment variables from .env
requests==2.31.0              # HTTP library (for health checks)
```

### Installing Individual Dependencies

If you want to install dependencies one by one:

```bash
# Core Framework
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"

# Database
pip install sqlalchemy==2.0.23
pip install psycopg2-binary==2.9.9

# Authentication
pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]==1.7.4"

# MQTT
pip install paho-mqtt==1.6.1

# Validation
pip install pydantic==2.5.0

# Utilities
pip install python-dotenv==1.0.0
pip install python-multipart==0.0.6
pip install requests==2.31.0
```

### Development Workflow

```bash
# 1. Make code changes in your editor

# 2. Backend auto-reloads (if using --reload flag)
#    No restart needed!

# 3. For frontend changes:
#    Just refresh browser (Ctrl + Shift + R)

# 4. To test changes:
#    - Check API docs: http://localhost:8000/docs
#    - Test frontend: http://localhost:3000
#    - View logs in terminal

# 5. Run tests (if you have them)
pytest

# 6. Check code quality
flake8 backend/
black backend/
```

---

## 🐳 Docker Build Process

Understanding how Docker images are built for this project.

### Docker Image Optimization

All services use **multi-stage builds** for smaller, more secure images:

#### Backend Dockerfile Explained

```dockerfile
# Stage 1: Builder - Install dependencies
FROM python:3.11-alpine as builder

WORKDIR /app

# Install build dependencies (gcc, etc.)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    linux-headers \
    libffi-dev

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Minimal image
FROM python:3.11-alpine

# Install only runtime dependencies
RUN apk add --no-cache \
    libpq \
    libffi

# Create non-root user for security
RUN addgroup -S appuser && adduser -S appuser -G appuser

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Set PATH for user packages
ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Why Multi-Stage?**
- **Builder stage**: Has all build tools (gcc, compilers) - ~400MB
- **Runtime stage**: Only has compiled packages and runtime libs - ~192MB
- **Savings**: 208MB (52% smaller!)

#### Frontend Dockerfile Explained

```dockerfile
# Stage 1: Prepare static files
FROM alpine:3.19 as builder

WORKDIR /build

# Copy all frontend files
COPY *.html ./
COPY *.js ./
COPY css/ ./css/
COPY js/ ./js/

# Remove unnecessary files
RUN find . -name "*.map" -type f -delete && \
    find . -name ".DS_Store" -type f -delete && \
    find . -name "Thumbs.db" -type f -delete

# Stage 2: Nginx runtime
FROM nginx:1.25-alpine

# Copy optimized files
COPY --from=builder /build /usr/share/nginx/html/

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html

USER nginx

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Building Individual Images

```bash
# Build backend image
docker build -t sensegrid-backend:latest -f backend/Dockerfile backend/

# Build frontend image
docker build -t sensegrid-frontend:latest -f frontend/Dockerfile frontend/

# Build frontend2 image
docker build -t sensegrid-frontend2:latest -f frontend2/Dockerfile frontend2/

# Build simulator image
docker build -t sensegrid-simulator:latest -f Dockerfile.simulator .

# View image sizes
docker images | grep sensegrid
```

### Docker Compose Build Process

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend

# Build with no cache (fresh build)
docker-compose build --no-cache

# Build and start
docker-compose up -d --build

# Build with progress output
docker-compose build --progress=plain
```

### Image Size Comparison

| Image | Base | Size | Optimization |
|-------|------|------|--------------|
| **Backend** | Alpine | 192MB | Multi-stage build |
| **Simulator** | Alpine | 84.6MB | Multi-stage build |
| **Frontend** | Nginx Alpine | 74.6MB | File cleanup |
| **Frontend2** | Nginx Alpine | 74.3MB | File cleanup |
| **Total** | - | **426MB** | 45% smaller than Debian |

### Custom Docker Build

If you want to customize the build:

```bash
# Build with custom tag
docker build -t my-sensegrid-backend:v2.0 backend/

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.12 -t backend:py312 backend/

# Build for different platform
docker build --platform linux/amd64 -t backend:amd64 backend/

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t backend:multi .
```

### Dockerfile Best Practices Used

1. **Multi-stage builds** - Separate build and runtime
2. **Alpine Linux** - Minimal base images
3. **Non-root users** - Security best practice
4. **Layer caching** - Ordered commands for better caching
5. **Health checks** - Container health monitoring
6. **Version pinning** - Reproducible builds
7. **Minimal dependencies** - Only install what's needed
8. **`.dockerignore`** - Exclude unnecessary files

### Docker Compose Services

```yaml
services:
  db:                    # TimescaleDB database
  backend:               # FastAPI application
  frontend:              # API dashboard (Nginx)
  frontend2:             # MQTT dashboard (Nginx)
  simulator:             # Sensor data simulator
```

### Build Order and Dependencies

```
1. db (TimescaleDB)
   ↓
2. backend (waits for db to be healthy)
   ↓
3. frontend, frontend2, simulator (wait for backend)
```

### Debugging Docker Builds

```bash
# Build with verbose output
docker-compose build --progress=plain

# Build and see each layer
docker build --progress=plain -t backend backend/

# Inspect image layers
docker history sensegrid-backend:latest

# Check image size breakdown
docker images sensegrid-backend --format "table {{.Repository}}\t{{.Size}}"

# Run intermediate build stage
docker build --target builder -t backend-builder backend/
docker run -it backend-builder sh
```

### Pushing to Docker Registry

```bash
# Tag images
docker tag sensegrid-backend:latest yourusername/sensegrid-backend:latest
docker tag sensegrid-backend:latest yourusername/sensegrid-backend:v1.0.0

# Login to Docker Hub
docker login

# Push images
docker push yourusername/sensegrid-backend:latest
docker push yourusername/sensegrid-backend:v1.0.0

# Pull images (on another machine)
docker pull yourusername/sensegrid-backend:latest
```


---

## ⚙️ Configuration

### Environment Variables

The platform uses environment variables for configuration. All variables are defined in `.env` file.

#### Database Configuration

```bash
# PostgreSQL/TimescaleDB
POSTGRES_USER=postgres          # Database username
POSTGRES_PASSWORD=postgres      # Database password
POSTGRES_DB=sensegrid_db       # Database name
DATABASE_PORT=5432             # Database port (default: 5432)
```

#### Backend Configuration

```bash
# FastAPI Backend
BACKEND_PORT=8000                                    # Backend port
DATABASE_URL=postgresql://postgres:postgres@db:5432/sensegrid_db
SECRET_KEY=your-secret-key-here                      # JWT secret
ALGORITHM=HS256                                      # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=30                       # Token expiry
```

#### MQTT Configuration

```bash
# MQTT Broker
MQTT_BROKER=broker.hivemq.com   # Public HiveMQ broker
MQTT_PORT=1883                  # MQTT port
MQTT_TOPIC_PREFIX=sensegrid     # Topic prefix for all messages
```

#### Frontend Configuration

```bash
# Frontend Ports
FRONTEND_PORT=3000              # API Dashboard port
FRONTEND2_PORT=3001             # MQTT Dashboard port
```

### Changing Configuration

1. Edit the `.env` file
2. Restart the services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## 📖 Usage

### Managing Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart backend

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Check service status
docker-compose ps
```

### Accessing the Database

```bash
# Connect to PostgreSQL
docker exec -it sensegrid-db psql -U postgres -d sensegrid_db

# Example queries
SELECT * FROM devices;
SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10;
```

### Running the Simulator Locally (Optional)

```bash
# If you want to run the simulator outside Docker
cd backend
python sensor_simulator.py
```

### Clearing All Data

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose up -d --build
```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "password123"
}
```

#### Login
```http
POST /api/v1/auth/signin
Content-Type: application/json

{
  "username": "john",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Device Endpoints

#### Get All Devices
```http
GET /api/v1/devices/
Authorization: Bearer <token>
```

#### Get Device Details
```http
GET /api/v1/devices/{device_id}
Authorization: Bearer <token>
```

#### Get Sensor Data
```http
GET /api/v1/devices/{device_id}/sensors/{sensor_type}/timeseries?hours=24
Authorization: Bearer <token>
```

### Interactive API Docs

Visit http://localhost:8000/docs for full interactive API documentation with:
- All endpoints listed
- Request/response schemas
- Try-it-out functionality
- Authentication support

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Services Not Starting**

**Problem**: `docker-compose up` fails

**Solution**:
```bash
# Check Docker is running
docker --version

# Check logs for errors
docker-compose logs

# Try rebuilding
docker-compose down
docker-compose up -d --build
```

#### 2. **Backend Shows "Unhealthy"**

**Problem**: Backend container is unhealthy

**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Common causes:
# - Database not ready: Wait 30 seconds and check again
# - Port conflict: Change BACKEND_PORT in .env
# - Database connection: Verify DATABASE_URL in .env
```

#### 3. **Frontend Not Loading**

**Problem**: Browser shows blank page or errors

**Solution**:
```bash
# Hard refresh browser
# Windows/Linux: Ctrl + Shift + R
# Mac: Cmd + Shift + R

# Or use incognito mode
# Chrome: Ctrl + Shift + N
```

#### 4. **No Sensor Data Showing**

**Problem**: Dashboards show "No data" or empty charts

**Solution**:
```bash
# Check if simulator is running
docker-compose ps

# Restart simulator
docker-compose restart simulator

# Check simulator logs
docker-compose logs simulator

# Verify MQTT connection
# Should see: "Connected to MQTT broker"
```

#### 5. **Database Connection Error**

**Problem**: Backend can't connect to database

**Solution**:
```bash
# Check if database is healthy
docker-compose ps

# Restart database
docker-compose restart db

# Wait for database to be ready (30 seconds)
docker-compose logs db
```

#### 6. **Port Already in Use**

**Problem**: Error: "port is already allocated"

**Solution**:
```bash
# Find what's using the port (example: port 8000)
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Option 1: Stop the conflicting service
# Option 2: Change port in .env file
BACKEND_PORT=8001
```

#### 7. **Settings Not Saving**

**Problem**: Refresh interval or time period resets

**Solution**:
- Clear browser cache
- Check browser console for errors (F12)
- Ensure localStorage is enabled
- Try a different browser

---

## 📁 Project Structure

```
Docker/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   └── v1/
│   │   │       ├── auth.py    # Authentication endpoints
│   │   │       ├── devices.py # Device endpoints
│   │   │       └── users.py   # User management
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT & password hashing
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── device.py
│   │   │   ├── sensor.py
│   │   │   └── user.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── device.py
│   │   │   ├── sensor.py
│   │   │   └── user.py
│   │   └── services/          # Business logic
│   │       ├── device_service.py
│   │       ├── mqtt_service.py
│   │       └── sensor_service.py
│   ├── Dockerfile             # Backend Docker image
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment variables template
│
├── frontend/                  # API Dashboard (Nginx)
│   ├── css/                   # Stylesheets
│   │   └── devices.css
│   ├── js/                    # JavaScript modules
│   │   ├── components/        # Reusable components
│   │   ├── devices-api.js     # API client
│   │   ├── devices-app.js     # Main application
│   │   └── devices-config.js  # Configuration
│   ├── index.html             # Login page
│   ├── signup.html            # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── devices-dashboard.html # Devices monitoring
│   ├── config.js              # API configuration
│   ├── nginx.conf             # Nginx configuration
│   └── Dockerfile             # Frontend Docker image
│
├── frontend2/                 # MQTT Dashboard (Nginx)
│   ├── css/
│   │   └── devices.css
│   ├── js/
│   │   └── mqtt-dashboard.js  # MQTT client & UI
│   ├── index.html             # MQTT dashboard page
│   ├── nginx.conf
│   └── Dockerfile
│
├── sensor_simulator.py        # IoT device simulator
├── Dockerfile.simulator       # Simulator Docker image
├── docker-compose.yml         # Docker orchestration
├── .env.example              # Environment template
├── .env                      # Your environment (gitignored)
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## 🔧 Advanced Configuration

### Using a Different MQTT Broker

To use your own MQTT broker instead of HiveMQ:

1. Edit `.env`:
   ```bash
   MQTT_BROKER=your-broker.com
   MQTT_PORT=1883
   MQTT_TOPIC_PREFIX=your-prefix
   ```

2. Update frontend2 MQTT connection:
   Edit `frontend2/js/mqtt-dashboard.js`:
   ```javascript
   const MQTT_CONFIG = {
       BROKER: 'wss://your-broker.com:8884/mqtt',
       TOPIC_PREFIX: 'your-prefix',
       // ...
   };
   ```

3. Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Adding More Devices

Edit `sensor_simulator.py`:

```python
DEVICES = {
    'LR1': {...},
    'LR2': {...},
    'LR3': {  # Add new device
        'name': 'Living Room 3',
        'location': 'Building A',
        'sensors': {
            'CT1': {...},
            # ...
        }
    }
}
```

### Changing Database Credentials

1. Edit `.env`:
   ```bash
   POSTGRES_USER=myuser
   POSTGRES_PASSWORD=mypassword
   POSTGRES_DB=mydb
   DATABASE_URL=postgresql://myuser:mypassword@db:5432/mydb
   ```

2. Remove old database volume:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

---

## 📊 Monitoring & Logs

### View Real-time Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f simulator

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Container Health

```bash
# List all containers with status
docker-compose ps

# Inspect specific container
docker inspect sensegrid-backend

# Check resource usage
docker stats
```

### Database Monitoring

```bash
# Connect to database
docker exec -it sensegrid-db psql -U postgres -d sensegrid_db

# Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Count sensor readings
SELECT COUNT(*) FROM sensor_readings;

# Recent readings
SELECT * FROM sensor_readings 
ORDER BY timestamp DESC 
LIMIT 10;
```

---

## 🔒 Security Notes

### Production Deployment

**⚠️ Important**: The default configuration is for development only!

For production:

1. **Change all default passwords**:
   ```bash
   POSTGRES_PASSWORD=<strong-random-password>
   SECRET_KEY=<generate-new-secret-key>
   ```

2. **Use HTTPS**:
   - Set up SSL certificates
   - Configure Nginx for HTTPS
   - Use secure MQTT (TLS)

3. **Restrict database access**:
   - Don't expose port 5432 publicly
   - Use firewall rules

4. **Enable CORS properly**:
   - Edit `backend/main.py`
   - Restrict allowed origins

5. **Use environment-specific configs**:
   - Separate `.env` files for dev/staging/prod
   - Never commit `.env` to Git

---

## 🤝 Support

### Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Review this README**: Most issues are covered
3. **Check Docker status**: `docker-compose ps`
4. **Verify environment**: Check `.env` file

### Useful Commands Cheat Sheet

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart one service
docker-compose restart backend

# Remove everything (including data!)
docker-compose down -v

# Check Docker images sizes
docker images docker-*
```

---

## 📝 License

This project is provided as-is for educational and development purposes.

---

## 🎉 Success!

If you've followed all the steps, you should now have:

- ✅ All services running in Docker
- ✅ API Dashboard at http://localhost:3000
- ✅ MQTT Dashboard at http://localhost:3001
- ✅ Real-time sensor data flowing
- ✅ Interactive API docs at http://localhost:8000/docs

**Enjoy monitoring your IoT devices!** 🚀

---

**Last Updated**: December 2024  
**Version**: 1.0.0
