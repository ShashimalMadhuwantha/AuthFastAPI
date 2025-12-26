# SenseGrid IoT Platform

A real-time IoT monitoring platform that helps you visualize sensor data from multiple devices. Built with FastAPI, TimescaleDB, and MQTT for efficient data handling.

![Platform](https://img.shields.io/badge/Platform-IoT-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)

---

## What's This About?

SenseGrid lets you monitor IoT sensor devices in real-time. Think of it as a dashboard for all your sensors - whether you're tracking temperature, current, or any other measurements. The platform handles everything from data collection to visualization.

**Key Features:**
- Two different dashboards (API-based and MQTT-based)
- Real-time data updates
- Historical data analysis
- User authentication
- Time-series database for efficient storage

---

## What You Get

### The Dashboards

**API Dashboard** (Port 3000)
This is your main dashboard. It pulls data from the REST API and lets you:
- See live sensor readings
- Adjust how often data refreshes (from 1 second to 5 minutes)
- View historical data (anywhere from 1 hour to 7 days)
- Requires login to access

**MQTT Dashboard** (Port 3001)
A simpler, real-time dashboard that:
- Connects directly to the MQTT broker
- Updates instantly when sensors publish data
- No login needed
- Great for monitoring live data streams

### Sensor Support

The platform works with these sensor types:
- **CT1/CT2** - Current transformers for measuring electrical current
- **IR** - Infrared temperature sensors
- **K-Type** - Thermocouple temperature sensors

---

## Getting Started with Docker

This is the easiest way to get everything running. You'll need Docker Desktop installed on your machine.

### What You Need

- Docker Desktop (version 20.10 or newer)
- At least 4GB of RAM
- About 2GB of free disk space

### Quick Setup

1. **Get the code**
```bash
git clone <your-repo-url>
cd AuthFastAPI
```

2. **Set up your environment**
```bash
cp .env.example .env
```
The default settings work fine for local development, so you don't need to change anything unless you want to.

3. **Start everything**
```bash
docker-compose --profile full up -d
```

Wait about 30-40 seconds for all services to start up. The backend needs a moment to connect to the database.

4. **Check if it's working**
```bash
docker-compose ps
```
You should see all containers running and healthy.

5. **Open your browser**
- Main dashboard: http://localhost:3000
- MQTT dashboard: http://localhost:3001
- API documentation: http://localhost:8000/docs

6. **Create your account**
- Go to http://localhost:3000
- Click "Sign Up"
- Fill in your details and you're good to go

### Using Docker Profiles

Here's where it gets interesting. You don't always need to run everything. Docker profiles let you start only what you need.

**Available profiles:**

- `core` - Just the database and backend API
- `frontend` - Database, backend, and both dashboards
- `simulator` - Database, backend, and the sensor simulator
- `dev` - Everything (recommended for development)
- `prod` - Everything except the simulator (for production)
- `full` - All services (same as dev)

**Examples:**

```bash
# Working on the backend? Start just the essentials
docker-compose --profile core up -d

# Need to test the UI? Add the frontends
docker-compose --profile frontend up -d

# Want to see simulated sensor data?
docker-compose --profile simulator up -d

# Full development setup
docker-compose --profile dev up -d

# Production deployment (no simulator)
docker-compose --profile prod up -d
```

**Useful commands:**

```bash
# Stop everything
docker-compose down

# See what's running
docker-compose ps

# Check the logs
docker-compose logs -f

# Restart a specific service
docker-compose restart backend

# Rebuild and restart
docker-compose --profile dev up -d --build

# Clean slate (removes data too!)
docker-compose down -v
```

### Docker Image Sizes

We've optimized the images using multi-stage builds and Alpine Linux:

| Service | Size | What We Did |
|---------|------|-------------|
| Backend | 192MB | Multi-stage build with Alpine |
| Simulator | 84.6MB | Stripped down to essentials |
| Frontend | 74.6MB | Nginx on Alpine |
| Frontend2 | 74.3MB | Nginx on Alpine |

Total: **426MB** (about 45% smaller than using standard Debian images)

---

## Developer Setup

Want to run things locally without Docker? Follow these steps to set up each component.

### Prerequisites

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **PostgreSQL 15+** - Choose your setup method below
- **Code Editor** - VS Code recommended

---

### Step 1: Database Setup

You have two options for the database:

#### Option A: Install PostgreSQL Locally (Recommended for Development)

**Windows:**
1. Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
2. Run the installer (remember the password you set!)
3. PostgreSQL will run on port 5432 by default

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Create the database:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Run these commands
CREATE DATABASE sensegrid_db;
CREATE USER sensegrid WITH PASSWORD 'sensegrid123';
GRANT ALL PRIVILEGES ON DATABASE sensegrid_db TO sensegrid;

# Optional: Enable TimescaleDB extension (if installed)
\c sensegrid_db
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Exit
\q
```

#### Option B: Use Docker for Database Only

If you don't want to install PostgreSQL locally, just run the database in Docker:

```bash
# Start only the database
docker run -d \
  --name sensegrid-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sensegrid_db \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg16

# Check if it's running
docker ps

# View logs
docker logs sensegrid-db

# Stop it later
docker stop sensegrid-db

# Start it again
docker start sensegrid-db

# Remove it completely
docker rm -f sensegrid-db
```

---

### Step 2: Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
# Create venv
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# You should see (venv) in your terminal now
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy example file
cp .env.example .env

# Now edit the .env file
```

**Edit `backend/.env` with these settings:**

```bash
# Database Configuration
DATABASE_URL=postgresql://sensegrid:sensegrid123@localhost:5432/sensegrid_db

# If using Docker database with default settings:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sensegrid_db

# Security (generate a new secret key for production!)
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT Configuration
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=sensegrid
```

5. **Run the backend**
```bash
# Make sure you're in the backend directory with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test it:** Open http://localhost:8000/docs in your browser

---

### Step 3: Frontend Setup (API Dashboard)

1. **Navigate to frontend directory**
```bash
# Open a NEW terminal
cd frontend
```

2. **Configure API endpoint**

Edit `frontend/config.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

This should already be set correctly, but verify it points to your backend.

3. **Serve the frontend**

**Option A: Python HTTP Server (Easiest)**
```bash
python -m http.server 3000
```

**Option B: Node.js HTTP Server**
```bash
# Install once globally
npm install -g http-server

# Run it
http-server -p 3000
```

**Option C: VS Code Live Server Extension**
- Install "Live Server" extension in VS Code
- Right-click `index.html` → "Open with Live Server"
- Change port to 3000 in settings if needed

**Access it:** http://localhost:3000

---

### Step 4: Frontend2 Setup (MQTT Dashboard)

1. **Navigate to frontend2 directory**
```bash
# Open another NEW terminal
cd frontend2
```

2. **Configure MQTT broker**

Edit `frontend2/js/mqtt-dashboard.js`:
```javascript
const MQTT_CONFIG = {
    BROKER: 'wss://broker.hivemq.com:8884/mqtt',  // WebSocket URL
    TOPIC_PREFIX: 'sensegrid',
    DEVICES: ['LR1', 'LR2'],
    SENSOR_TYPES: ['CT1', 'CT2', 'IR', 'K-Type']
};
```

This should already be configured, but verify the broker URL is correct.

3. **Serve the frontend**
```bash
python -m http.server 3001
```

**Access it:** http://localhost:3001

---

### Step 5: Simulator Setup (Required for Testing)

**Important:** The simulator is **essential for testing** the dashboard and backend. Without it, you won't see any sensor data flowing through the system.

The simulator generates realistic sensor data (temperature, current) and publishes it via MQTT, allowing you to:
- ✅ Test the **API Dashboard** (real-time charts and device status)
- ✅ Test the **MQTT Dashboard** (live sensor readings)
- ✅ Verify **device online/offline** detection
- ✅ See **historical data** and time-series graphs
- ✅ Test **MQTT message handling** in the backend


1. **Navigate to project root**
```bash
# Open another NEW terminal
cd AuthFastAPI
```

2. **Activate backend's virtual environment**
```bash
# Windows:
backend\venv\Scripts\activate

# Mac/Linux:
source backend/venv/bin/activate
```

3. **Run the simulator**
```bash
python sensor_simulator.py
```

You should see:
```
============================================================
IoT Sensor Data Simulator
============================================================
MQTT Broker: broker.hivemq.com:1883
Topic Prefix: sensegrid
Devices: LR1, LR2
============================================================

[LR1] Connected to MQTT broker
[LR1] Sent Birth message: online
[LR1] CT1: 2.45 A
[LR1] CT2: 3.12 A
...
```

---

### What You Should Have Running

After completing all steps, you should have these terminals open:

| Terminal | Command | URL | Status |
|----------|---------|-----|--------|
| 1 | `uvicorn main:app --reload` | http://localhost:8000 | ✅ Required |
| 2 | `python -m http.server 3000` | http://localhost:3000 | ✅ Required |
| 3 | `python -m http.server 3001` | http://localhost:3001 | ✅ Required |
| 4 | `python sensor_simulator.py` | - | ✅ **Required for Testing** |

Plus PostgreSQL running (either locally or in Docker).

**Note:** Without the simulator (Terminal 4), the dashboards will show no data!

---

### Development Workflow

**Making changes:**

1. **Backend changes** - Save the file, uvicorn auto-reloads
2. **Frontend changes** - Save and refresh browser (Ctrl+Shift+R)
3. **Database changes** - Restart backend to apply migrations

**Stopping everything:**
- Press `Ctrl+C` in each terminal
- If using Docker database: `docker stop sensegrid-db`

**Starting again:**
- Run the same commands in each terminal
- If using Docker database: `docker start sensegrid-db`

---

### Python Dependencies Explained

Here's what each package in `requirements.txt` does:

```txt
# Web Framework
fastapi==0.104.1              # Modern async web framework
uvicorn[standard]==0.24.0     # ASGI server to run FastAPI

# Database
sqlalchemy==2.0.23            # ORM for database operations
psycopg2-binary==2.9.9        # PostgreSQL adapter

# Authentication & Security
python-jose[cryptography]==3.3.0  # JWT token handling
passlib[bcrypt]==1.7.4        # Password hashing

# MQTT
paho-mqtt==1.6.1              # MQTT client library

# Data Validation
pydantic==2.5.0               # Request/response validation

# Utilities
python-dotenv==1.0.0          # Load .env files
python-multipart==0.0.6       # Handle file uploads
requests==2.31.0              # HTTP client for health checks
```

---

### Troubleshooting Local Development

**Backend won't start:**
```bash
# Check if port 8000 is in use
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# Try a different port
uvicorn main:app --reload --port 8001
```

**Can't connect to database:**
```bash
# Test PostgreSQL connection
psql -U sensegrid -d sensegrid_db -h localhost

# Check if PostgreSQL is running
# Windows: Check Services
# Mac: brew services list
# Linux: sudo systemctl status postgresql
```

**Frontend can't reach backend:**
- Check `config.js` has correct backend URL
- Make sure backend is running on port 8000
- Check browser console for CORS errors

**Simulator not publishing data:**
- Check MQTT broker is accessible
- Verify `MQTT_BROKER` in environment
- Check simulator logs for connection errors
pydantic==2.5.0               # Validate data

# Utilities
python-dotenv==1.0.0          # Load .env files
python-multipart==0.0.6       # Handle file uploads
requests==2.31.0              # Make HTTP requests
```

---

## Environment Files Guide

The project uses `.env` files for configuration. Here's what each one does and how to configure them.

### Overview of .env Files

```
AuthFastAPI/
├── .env                    # Docker Compose configuration (root level)
├── .env.example           # Template for root .env
└── backend/
    ├── .env              # Backend application configuration
    └── .env.example      # Template for backend .env
```

**Note:** Frontend and Frontend2 don't have `.env` files. They use:
- **Port mapping**: Configured in root `.env` (`FRONTEND_PORT`, `FRONTEND2_PORT`)
- **API URL**: Auto-detected in `config.js` (hardcoded logic)
- **MQTT Broker**: Hardcoded in `mqtt-dashboard.js`


---

### 1. Root `.env` (Docker Compose)

**Location:** `AuthFastAPI/.env`

**Purpose:** Used by `docker-compose.yml` to configure all Docker containers.

**When to use:** When running with Docker (`docker-compose up`)

**Setup:**
```bash
# Copy the example file
cp .env.example .env
```

**Configuration:**

```bash
# Database Configuration
POSTGRES_USER=postgres              # PostgreSQL username
POSTGRES_PASSWORD=postgres          # PostgreSQL password (CHANGE IN PRODUCTION!)
POSTGRES_DB=sensegrid_db           # Database name

# Backend Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/sensegrid_db
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT Configuration
MQTT_BROKER=broker.hivemq.com      # MQTT broker address
MQTT_PORT=1883                      # MQTT port
MQTT_TOPIC_PREFIX=sensegrid         # Topic prefix for all messages

# Application Ports
BACKEND_PORT=8000                   # Backend API port
FRONTEND_PORT=3000                  # API Dashboard port
FRONTEND2_PORT=3001                 # MQTT Dashboard port
DATABASE_PORT=5432                  # PostgreSQL port
```

**Important Notes:**
- `DATABASE_URL` uses `@db:5432` because Docker containers communicate via service names
- All services read from this file when running in Docker
- Port mappings: `HOST_PORT:CONTAINER_PORT`

---

### 2. Backend `.env`

**Location:** `AuthFastAPI/backend/.env`

**Purpose:** Used by the FastAPI backend application (both Docker and local development).

**When to use:** 
- Local development (running backend outside Docker)
- Docker also reads this, but root `.env` takes precedence

**Setup:**
```bash
cd backend
cp .env.example .env
```

**Configuration:**

```bash
# Database Configuration
# For LOCAL development:
DATABASE_URL=postgresql://sensegrid:sensegrid123@localhost:5432/sensegrid_db

# For Docker database only:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sensegrid_db

# For full Docker setup (use root .env instead):
# DATABASE_URL=postgresql://postgres:postgres@db:5432/sensegrid_db

# JWT Authentication
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT Configuration
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=sensegrid

# Application Settings
APP_PORT=8000

# PgAdmin Configuration (Optional)
PGADMIN_EMAIL=admin@sensegrid.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
```

**Key Differences from Root .env:**
- `DATABASE_URL` uses `@localhost:5432` for local development
- Includes PgAdmin settings (optional database management tool)
- More detailed comments for developers

**How to generate a secure SECRET_KEY:**
```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Configuration Scenarios

#### Scenario 1: Full Docker Setup (Recommended for Beginners)

**Use:** Root `.env` only

```bash
# 1. Configure root .env
cp .env.example .env

# 2. Start everything
docker-compose --profile full up -d
```

**Settings:**
- `DATABASE_URL` with `@db:5432` (Docker service name)
- All ports as needed
- Default credentials are fine for development

---

#### Scenario 2: Local Development (No Docker)

**Use:** Backend `.env` only

```bash
# 1. Configure backend .env
cd backend
cp .env.example .env

# 2. Edit backend/.env
# Set DATABASE_URL=postgresql://sensegrid:sensegrid123@localhost:5432/sensegrid_db

# 3. Run backend
uvicorn main:app --reload
```

**Settings:**
- `DATABASE_URL` with `@localhost:5432`
- Local PostgreSQL credentials
- Generate new `SECRET_KEY`

---

#### Scenario 3: Hybrid (Docker Database + Local Backend)

**Use:** Root `.env` for database, Backend `.env` for application

```bash
# 1. Start database only
docker-compose --profile core up -d db

# 2. Configure backend .env
cd backend
cp .env.example .env

# 3. Edit backend/.env
# Set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sensegrid_db

# 4. Run backend locally
uvicorn main:app --reload
```

**Settings:**
- Backend `.env` uses `@localhost:5432` (Docker database exposed on host)
- Use same credentials as root `.env`

---

### Environment Variables Reference

#### Database Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | Database name | `sensegrid_db` |
| `DATABASE_URL` | Full connection string | `postgresql://user:pass@host:port/db` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |

#### Security Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `09d25e094faa6ca...` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |

#### MQTT Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MQTT_BROKER` | MQTT broker address | `broker.hivemq.com` |
| `MQTT_PORT` | MQTT port | `1883` |
| `MQTT_TOPIC_PREFIX` | Topic prefix | `sensegrid` |

#### Port Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKEND_PORT` | Backend API port | `8000` |
| `FRONTEND_PORT` | API Dashboard port | `3000` |
| `FRONTEND2_PORT` | MQTT Dashboard port | `3001` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |

---

### Best Practices

1. **Never commit `.env` files to Git**
   - They're in `.gitignore` by default
   - Only commit `.env.example` files

2. **Use different credentials for production**
   - Change `POSTGRES_PASSWORD`
   - Generate new `SECRET_KEY`
   - Use strong passwords

3. **Keep `.env.example` updated**
   - When adding new variables, update the example
   - Add comments explaining each variable

4. **Use environment-specific files**
   - `.env.dev` for development
   - `.env.prod` for production
   - `.env.test` for testing

5. **Validate your configuration**
   ```bash
   # Check if backend can connect to database
   docker-compose logs backend
   
   # Test database connection
   psql -U postgres -d sensegrid_db -h localhost
   ```

---

### Troubleshooting .env Issues

**Backend can't connect to database:**
```bash
# Check DATABASE_URL format
# Should be: postgresql://username:password@host:port/database

# For Docker: @db:5432
# For Local: @localhost:5432
```

**Port conflicts:**
```bash
# Change ports in .env
BACKEND_PORT=8001
FRONTEND_PORT=3001

# Restart services
docker-compose down
docker-compose --profile dev up -d
```

**Changes not taking effect:**
```bash
# Restart Docker containers
docker-compose down
docker-compose --profile dev up -d

# For local development, restart the service
# Ctrl+C and run again
```

**Can't find .env file:**
```bash
# Create from example
cp .env.example .env

# Check if it exists
ls -la .env

# Windows:
dir .env
```

---

## Configuration

All settings are in the `.env` file. Here's what you can configure:

```bash
# Database settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sensegrid_db
DATABASE_PORT=5432

# Backend settings
BACKEND_PORT=8000
DATABASE_URL=postgresql://postgres:postgres@db:5432/sensegrid_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT settings
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=sensegrid

# Frontend ports
FRONTEND_PORT=3000
FRONTEND2_PORT=3001
```

To change any setting, just edit the `.env` file and restart:
```bash
docker-compose down
docker-compose --profile dev up -d
```

---

## API Documentation

The backend provides a REST API for everything. Once it's running, check out the interactive docs at http://localhost:8000/docs

### Quick Examples

**Sign up:**
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "password123"
}
```

**Log in:**
```http
POST /api/v1/auth/signin
Content-Type: application/json

{
  "username": "john",
  "password": "password123"
}
```

**Get all devices:**
```http
GET /api/v1/devices/
Authorization: Bearer <your-token>
```

**Get sensor data:**
```http
GET /api/v1/devices/LR1/sensors/CT1/timeseries?hours=24
Authorization: Bearer <your-token>
```

The interactive docs let you try all of this right in your browser. Much easier than using curl!

---

## Project Structure

Here's how everything is organized:

```
AuthFastAPI/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   ├── core/              # Config and security
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Data validation
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
├── sensor_simulator.py         # Generates fake sensor data
├── Dockerfile.simulator
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Common Issues

### Services won't start

Check the logs to see what's wrong:
```bash
docker-compose logs -f
```

Usually it's either the database taking too long to start, or a port conflict.

### Backend shows as "unhealthy"

Give it a minute. The backend waits for the database to be ready, which can take 30-40 seconds on first startup.

### Frontend shows a blank page

Hard refresh your browser (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac). 
### No sensor data appearing

Make sure the simulator is running:
```bash
docker-compose logs simulator
```

You should see it connecting to MQTT and publishing data every second.

### Port already in use

Something else is using one of the ports. Either stop that service, or change the port in `.env`:
```bash
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

---

## Security Notes

**Important:** The default configuration is for development only!

For production:
- Change all passwords in `.env`
- Generate a new `SECRET_KEY`
- Use HTTPS
- Don't expose the database port publicly
- Set up proper CORS settings in the backend

---


## License

This project is provided as-is for educational and development purposes.

---

**Questions?** Check the logs first (`docker-compose logs -f`), they usually tell you what's wrong.

**Version:** 1.0.0  
**Last Updated:** December 2024
