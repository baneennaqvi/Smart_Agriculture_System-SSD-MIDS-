from pydantic import BaseModel, EmailStr, field_validator, constr
from datetime import datetime
from enum import Enum
from typing import Optional, List
import re

# Validation patterns
ALPHABETIC_PATTERN = r'^[a-zA-Z\s]+$'
ALPHANUMERIC_PATTERN = r'^[a-zA-Z0-9\s]+$'
LOCATION_PATTERN = r'^[a-zA-Z\s]+$'
BLOCKCHAIN_HASH_PATTERN = r'^[a-zA-Z0-9]{10}$'
PEST_DISEASE_PATTERN = r'^[a-zA-Z0-9\s]{10,}$'

class UserRole(str, Enum):
    farmer = "farmer"
    admin = "admin"
    operator = "operator"

class UserBase(BaseModel):
    name: constr(min_length=2, max_length=50, pattern=ALPHABETIC_PATTERN)
    email: EmailStr
    role: UserRole
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(ALPHABETIC_PATTERN, v):
            raise ValueError("Name must contain only alphabets and spaces")
        return v

class UserCreate(UserBase):
    password: constr(min_length=8, max_length=50)

class User(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SensorType(str, Enum):
    temperature = "temperature"
    humidity = "humidity"
    soil_moisture = "soil_moisture"
    ph = "pH"

class SensorStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    faulty = "faulty"

class SensorBase(BaseModel):
    type: SensorType
    location: constr(min_length=3, max_length=100, pattern=LOCATION_PATTERN)
    status: SensorStatus

    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        if not re.match(LOCATION_PATTERN, v):
            raise ValueError("Location must contain only alphabets and spaces")
        return v

class SensorCreate(SensorBase):
    pass

class Sensor(SensorBase):
    sensor_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class SensorDataBase(BaseModel):
    sensor_id: int
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    ph_level: Optional[float] = None

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and (v < -50 or v > 60):
            raise ValueError("Temperature must be between -50 and 60°C")
        return v

    @field_validator('humidity')
    @classmethod
    def validate_humidity(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Humidity must be between 0 and 100%")
        return v

    @field_validator('soil_moisture')
    @classmethod
    def validate_soil_moisture(cls, v):
        if v is not None and v < 0:
            raise ValueError("Soil moisture cannot be negative")
        return v

    @field_validator('ph_level')
    @classmethod
    def validate_ph_level(cls, v):
        if v is not None and (v < 0 or v > 14):
            raise ValueError("pH level must be between 0 and 14")
        return v

class SensorDataCreate(SensorDataBase):
    pass

class SensorData(SensorDataBase):
    data_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class IrrigationStatus(str, Enum):
    on = "on"
    off = "off"

class IrrigationSystemBase(BaseModel):
    farm_id: int
    status: IrrigationStatus
    water_usage: float = 0.0

    @field_validator('farm_id')
    @classmethod
    def validate_farm_id(cls, v):
        if v <= 0:
            raise ValueError("Farm ID must be a positive number")
        return v

    @field_validator('water_usage')
    @classmethod
    def validate_water_usage(cls, v):
        if v < 0:
            raise ValueError("Water usage cannot be negative")
        return v

class IrrigationSystemCreate(IrrigationSystemBase):
    pass

class IrrigationSystem(IrrigationSystemBase):
    irrigation_id: int
    last_activated: datetime
    
    class Config:
        from_attributes = True

class WeatherDataBase(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v < -50 or v > 60:
            raise ValueError("Temperature must be between -50 and 60°C")
        return v

    @field_validator('humidity')
    @classmethod
    def validate_humidity(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Humidity must be between 0 and 100%")
        return v

    @field_validator('rainfall')
    @classmethod
    def validate_rainfall(cls, v):
        if v < 0:
            raise ValueError("Rainfall cannot be negative")
        return v

    @field_validator('wind_speed')
    @classmethod
    def validate_wind_speed(cls, v):
        if v < 0:
            raise ValueError("Wind speed cannot be negative")
        return v

class WeatherDataCreate(WeatherDataBase):
    pass

class WeatherData(WeatherDataBase):
    weather_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class CropStatus(str, Enum):
    planted = "planted"
    growing = "growing"
    ready_for_harvest = "ready_for_harvest"
    harvested = "harvested"

class CropManagementBase(BaseModel):
    name: constr(min_length=2, max_length=100, pattern=ALPHABETIC_PATTERN)
    planting_date: datetime
    harvest_date: Optional[datetime] = None
    expected_yield: Optional[float] = None
    status: CropStatus

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(ALPHABETIC_PATTERN, v):
            raise ValueError("Crop name must contain only alphabets and spaces")
        return v

    @field_validator('expected_yield')
    @classmethod
    def validate_expected_yield(cls, v):
        if v is not None and v < 0:
            raise ValueError("Expected yield cannot be negative")
        return v

class CropManagementCreate(CropManagementBase):
    pass

class CropManagement(CropManagementBase):
    crop_id: int
    
    class Config:
        from_attributes = True

class FertilizationStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"

class FertilizationSystemBase(BaseModel):
    farm_id: int
    status: FertilizationStatus
    nutrient_type: constr(min_length=2, max_length=50, pattern=ALPHANUMERIC_PATTERN)

    @field_validator('farm_id')
    @classmethod
    def validate_farm_id(cls, v):
        if v <= 0:
            raise ValueError("Farm ID must be a positive number")
        return v

    @field_validator('nutrient_type')
    @classmethod
    def validate_nutrient_type(cls, v):
        if not re.match(ALPHANUMERIC_PATTERN, v):
            raise ValueError("Nutrient type must contain only letters, numbers, and spaces")
        return v

class FertilizationSystemCreate(FertilizationSystemBase):
    pass

class FertilizationSystem(FertilizationSystemBase):
    fertilization_id: int
    last_fertilized: datetime
    
    class Config:
        from_attributes = True

class PestDiseaseDetectionBase(BaseModel):
    crop_id: int
    symptom_detected: constr(min_length=10, max_length=255, pattern=PEST_DISEASE_PATTERN)
    diagnosis: constr(min_length=10, max_length=1000, pattern=PEST_DISEASE_PATTERN)
    recommended_action: constr(min_length=10, max_length=1000, pattern=PEST_DISEASE_PATTERN)

    @field_validator('crop_id')
    @classmethod
    def validate_crop_id(cls, v):
        if v <= 0:
            raise ValueError("Crop ID must be a positive number")
        return v

    @field_validator('symptom_detected', 'diagnosis', 'recommended_action')
    @classmethod
    def validate_text_fields(cls, v):
        if not re.match(PEST_DISEASE_PATTERN, v):
            raise ValueError("Field must contain at least 10 characters and can include letters, numbers, and spaces")
        return v

class PestDiseaseDetectionCreate(PestDiseaseDetectionBase):
    pass

class PestDiseaseDetection(PestDiseaseDetectionBase):
    detection_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class TransactionType(str, Enum):
    harvest = "harvest"
    transport = "transport"
    storage = "storage"
    sale = "sale"
    purchase = "purchase"

class SupplyChainTransactionBase(BaseModel):
    crop_id: int
    transaction_type: TransactionType
    quantity: float
    price: Optional[float] = None
    from_location: constr(min_length=3, max_length=255, pattern=LOCATION_PATTERN)
    to_location: constr(min_length=3, max_length=255, pattern=LOCATION_PATTERN)
    blockchain_hash: constr(pattern=BLOCKCHAIN_HASH_PATTERN)
    status: constr(min_length=2, max_length=50, pattern=ALPHANUMERIC_PATTERN)

    @field_validator('crop_id')
    @classmethod
    def validate_crop_id(cls, v):
        if v <= 0:
            raise ValueError("Crop ID must be a positive number")
        return v

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator('from_location', 'to_location')
    @classmethod
    def validate_location(cls, v):
        if not re.match(LOCATION_PATTERN, v):
            raise ValueError("Location must contain only alphabets and spaces")
        return v

    @field_validator('blockchain_hash')
    @classmethod
    def validate_blockchain_hash(cls, v):
        if not re.match(BLOCKCHAIN_HASH_PATTERN, v):
            raise ValueError("Blockchain hash must be a 10-character hexadecimal string")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if not re.match(ALPHANUMERIC_PATTERN, v):
            raise ValueError("Status must contain only letters, numbers, and spaces")
        return v

class SupplyChainTransactionCreate(SupplyChainTransactionBase):
    pass

class SupplyChainTransaction(SupplyChainTransactionBase):
    transaction_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str