from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, users, devices, retention, quota
from app.db.database import engine, Base
from app.core.logger import logger
from app.services.mqtt_service import mqtt_service
from contextlib import asynccontextmanager

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")
    
    logger.info("Starting MQTT service...")
    mqtt_service.start()
    logger.info("MQTT service started")
    
    yield
    
    # Shutdown
    logger.info("Stopping MQTT service...")
    mqtt_service.stop()
    logger.info("MQTT service stopped")

app = FastAPI(
    title="IoT Device Management API",
    description="Authentication API with JWT and IoT Device/Sensor Management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["User Management"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices & Sensors"])
app.include_router(retention.router, prefix="/api/v1/retention", tags=["Data Retention"])
app.include_router(quota.router, prefix="/api/v1/quota", tags=["Data Quota"])

logger.info("FastAPI application started successfully")

@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {
        "message": "Hello world",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    mqtt_status = "connected" if mqtt_service.connected else "disconnected"
    return {
        "status": "healthy",
        "mqtt": mqtt_status
    }
