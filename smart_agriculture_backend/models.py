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
    hashed_password = Column(String(255), nullable=False)
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

class IrrigationStatus(str, enum.Enum):
    on = "on"
    off = "off"

class IrrigationSystem(Base):
    __tablename__ = "irrigation_systems"
    
    irrigation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, nullable=False)
    status = Column(Enum(IrrigationStatus), nullable=False)
    last_activated = Column(TIMESTAMP, server_default=func.now())
    water_usage = Column(Float, default=0.0)

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    weather_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())

class CropStatus(str, enum.Enum):
    planted = "planted"
    growing = "growing"
    ready_for_harvest = "ready_for_harvest"
    harvested = "harvested"

class CropManagement(Base):
    __tablename__ = "crop_management"
    
    crop_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    planting_date = Column(TIMESTAMP, nullable=False)
    harvest_date = Column(TIMESTAMP)
    expected_yield = Column(Float)
    status = Column(Enum(CropStatus), nullable=False)

class FertilizationStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"

class FertilizationSystem(Base):
    __tablename__ = "fertilization_systems"
    
    fertilization_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, nullable=False)
    status = Column(Enum(FertilizationStatus), nullable=False)
    last_fertilized = Column(TIMESTAMP, server_default=func.now())
    nutrient_type = Column(String(255), nullable=False)

class PestDiseaseDetection(Base):
    __tablename__ = "pest_disease_detections"
    
    detection_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crop_id = Column(Integer, ForeignKey("crop_management.crop_id"), nullable=False)
    symptom_detected = Column(String(255), nullable=False)
    diagnosis = Column(String(1000), nullable=False)
    recommended_action = Column(String(1000), nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())

class TransactionType(str, enum.Enum):
    harvest = "harvest"
    transport = "transport"
    storage = "storage"
    sale = "sale"
    purchase = "purchase"

class SupplyChainTransaction(Base):
    __tablename__ = "supply_chain_transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crop_id = Column(Integer, ForeignKey("crop_management.crop_id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float)
    from_location = Column(String(255), nullable=False)
    to_location = Column(String(255), nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    blockchain_hash = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False)