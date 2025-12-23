"""
Clear all devices and sensor readings from the database
Run this to start fresh with a clean database
"""

from app.db.database import SessionLocal, engine
from app.models.sensor import Device, SensorReading, Base

def clear_database():
    """Remove all devices and sensor readings"""
    db = SessionLocal()
    try:
        # Delete all sensor readings first (due to foreign key constraint)
        deleted_readings = db.query(SensorReading).delete()
        print(f"Deleted {deleted_readings} sensor readings")
        
        # Delete all devices
        deleted_devices = db.query(Device).delete()
        print(f"Deleted {deleted_devices} devices")
        
        db.commit()
        print("\n✅ Database cleared successfully!")
        print("You can now run the simulator to create LR1 and LR2 devices fresh.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Cleanup Script")
    print("=" * 60)
    print("This will delete ALL devices and sensor readings.")
    print("=" * 60)
    print()
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() == "yes":
        clear_database()
    else:
        print("Operation cancelled.")
