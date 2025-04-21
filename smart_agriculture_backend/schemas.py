from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    farmer = "farmer"
    admin = "admin"
    operator = "operator"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

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
    location: str
    status: SensorStatus

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
    def validate_temperature(cls, v):
        if v is not None and (v < -50 or v > 60):
            raise ValueError("Temperature must be between -50 and 60°C")
        return v

    @field_validator('humidity')
    def validate_humidity(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Humidity must be between 0 and 100%")
        return v

    @field_validator('soil_moisture')
    def validate_soil_moisture(cls, v):
        if v is not None and v < 0:
            raise ValueError("Soil moisture cannot be negative")
        return v

    @field_validator('ph_level')
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