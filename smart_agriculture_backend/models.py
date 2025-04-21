from sqlalchemy import Column, Integer, String, Float, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    farmer = "farmer"
    admin = "admin"
    operator = "operator"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class SensorType(str, enum.Enum):
    temperature = "temperature"
    humidity = "humidity"
    soil_moisture = "soil_moisture"
    ph = "pH"

class SensorStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    faulty = "faulty"

class Sensor(Base):
    __tablename__ = "sensors"
    
    sensor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(Enum(SensorType), nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(Enum(SensorStatus), nullable=False)
    last_updated = Column(TIMESTAMP, server_default=func.now())

class SensorData(Base):
    __tablename__ = "sensor_data"
    
    data_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey("sensors.sensor_id"), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    soil_moisture = Column(Float)
    ph_level = Column(Float)
    timestamp = Column(TIMESTAMP, server_default=func.now())