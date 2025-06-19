from sqlalchemy.orm import Session
import models
import schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_sensor(db: Session, sensor_id: int):
    return db.query(models.Sensor).filter(models.Sensor.sensor_id == sensor_id).first()

def get_sensors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sensor).offset(skip).limit(limit).all()

def create_sensor(db: Session, sensor: schemas.SensorCreate):
    db_sensor = models.Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def get_sensor_data(db: Session, data_id: int):
    return db.query(models.SensorData).filter(models.SensorData.data_id == data_id).first()

def get_all_sensor_data(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SensorData).offset(skip).limit(limit).all()

def get_sensor_data_by_sensor(db: Session, sensor_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SensorData).filter(models.SensorData.sensor_id == sensor_id).offset(skip).limit(limit).all()

def create_sensor_data(db: Session, sensor_data: schemas.SensorDataCreate):
    db_sensor_data = models.SensorData(**sensor_data.model_dump())
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data

def update_sensor_data(db: Session, data_id: int, sensor_data: schemas.SensorDataCreate):
    db_sensor_data = get_sensor_data(db, data_id)
    if db_sensor_data:
        for key, value in sensor_data.model_dump().items():
            setattr(db_sensor_data, key, value)
        db.commit()
        db.refresh(db_sensor_data)
    return db_sensor_data

def delete_sensor_data(db: Session, data_id: int):
    db_sensor_data = get_sensor_data(db, data_id)
    if db_sensor_data:
        db.delete(db_sensor_data)
        db.commit()
    return db_sensor_data

# Irrigation System CRUD operations
def get_irrigation_system(db: Session, irrigation_id: int):
    return db.query(models.IrrigationSystem).filter(models.IrrigationSystem.irrigation_id == irrigation_id).first()

def get_irrigation_systems(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.IrrigationSystem).offset(skip).limit(limit).all()

def get_irrigation_systems_by_farm(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.IrrigationSystem).filter(models.IrrigationSystem.farm_id == farm_id).offset(skip).limit(limit).all()

def create_irrigation_system(db: Session, irrigation: schemas.IrrigationSystemCreate):
    db_irrigation = models.IrrigationSystem(**irrigation.model_dump())
    db.add(db_irrigation)
    db.commit()
    db.refresh(db_irrigation)
    return db_irrigation

def update_irrigation_system(db: Session, irrigation_id: int, irrigation: schemas.IrrigationSystemCreate):
    db_irrigation = get_irrigation_system(db, irrigation_id)
    if db_irrigation:
        for key, value in irrigation.model_dump().items():
            setattr(db_irrigation, key, value)
        db.commit()
        db.refresh(db_irrigation)
    return db_irrigation

def delete_irrigation_system(db: Session, irrigation_id: int):
    db_irrigation = get_irrigation_system(db, irrigation_id)
    if db_irrigation:
        db.delete(db_irrigation)
        db.commit()
    return db_irrigation

# Weather Data CRUD operations
def get_weather_data(db: Session, weather_id: int):
    return db.query(models.WeatherData).filter(models.WeatherData.weather_id == weather_id).first()

def get_weather_data_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.WeatherData).offset(skip).limit(limit).all()

def create_weather_data(db: Session, weather: schemas.WeatherDataCreate):
    db_weather = models.WeatherData(**weather.model_dump())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

def update_weather_data(db: Session, weather_id: int, weather: schemas.WeatherDataCreate):
    db_weather = get_weather_data(db, weather_id)
    if db_weather:
        for key, value in weather.model_dump().items():
            setattr(db_weather, key, value)
        db.commit()
        db.refresh(db_weather)
    return db_weather

def delete_weather_data(db: Session, weather_id: int):
    db_weather = get_weather_data(db, weather_id)
    if db_weather:
        db.delete(db_weather)
        db.commit()
    return db_weather

# Crop Management CRUD operations
def get_crop(db: Session, crop_id: int):
    return db.query(models.CropManagement).filter(models.CropManagement.crop_id == crop_id).first()

def get_crops(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CropManagement).offset(skip).limit(limit).all()

def create_crop(db: Session, crop: schemas.CropManagementCreate):
    db_crop = models.CropManagement(**crop.model_dump())
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return db_crop

def update_crop(db: Session, crop_id: int, crop: schemas.CropManagementCreate):
    db_crop = get_crop(db, crop_id)
    if db_crop:
        for key, value in crop.model_dump().items():
            setattr(db_crop, key, value)
        db.commit()
        db.refresh(db_crop)
    return db_crop

def delete_crop(db: Session, crop_id: int):
    db_crop = get_crop(db, crop_id)
    if db_crop:
        db.delete(db_crop)
        db.commit()
    return db_crop

# Fertilization System CRUD operations
def get_fertilization_system(db: Session, fertilization_id: int):
    return db.query(models.FertilizationSystem).filter(models.FertilizationSystem.fertilization_id == fertilization_id).first()

def get_fertilization_systems(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FertilizationSystem).offset(skip).limit(limit).all()

def get_fertilization_systems_by_farm(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FertilizationSystem).filter(models.FertilizationSystem.farm_id == farm_id).offset(skip).limit(limit).all()

def create_fertilization_system(db: Session, fertilization: schemas.FertilizationSystemCreate):
    db_fertilization = models.FertilizationSystem(**fertilization.model_dump())
    db.add(db_fertilization)
    db.commit()
    db.refresh(db_fertilization)
    return db_fertilization

def update_fertilization_system(db: Session, fertilization_id: int, fertilization: schemas.FertilizationSystemCreate):
    db_fertilization = get_fertilization_system(db, fertilization_id)
    if db_fertilization:
        for key, value in fertilization.model_dump().items():
            setattr(db_fertilization, key, value)
        db.commit()
        db.refresh(db_fertilization)
    return db_fertilization

def delete_fertilization_system(db: Session, fertilization_id: int):
    db_fertilization = get_fertilization_system(db, fertilization_id)
    if db_fertilization:
        db.delete(db_fertilization)
        db.commit()
    return db_fertilization

# Pest & Disease Detection CRUD operations
def get_pest_disease_detection(db: Session, detection_id: int):
    return db.query(models.PestDiseaseDetection).filter(models.PestDiseaseDetection.detection_id == detection_id).first()

def get_pest_disease_detections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PestDiseaseDetection).offset(skip).limit(limit).all()

def get_pest_disease_detections_by_crop(db: Session, crop_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.PestDiseaseDetection).filter(models.PestDiseaseDetection.crop_id == crop_id).offset(skip).limit(limit).all()

def create_pest_disease_detection(db: Session, detection: schemas.PestDiseaseDetectionCreate):
    db_detection = models.PestDiseaseDetection(**detection.model_dump())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

def update_pest_disease_detection(db: Session, detection_id: int, detection: schemas.PestDiseaseDetectionCreate):
    db_detection = get_pest_disease_detection(db, detection_id)
    if db_detection:
        for key, value in detection.model_dump().items():
            setattr(db_detection, key, value)
        db.commit()
        db.refresh(db_detection)
    return db_detection

def delete_pest_disease_detection(db: Session, detection_id: int):
    db_detection = get_pest_disease_detection(db, detection_id)
    if db_detection:
        db.delete(db_detection)
        db.commit()
    return db_detection

# Supply Chain Transaction CRUD operations
def get_supply_chain_transaction(db: Session, transaction_id: int):
    return db.query(models.SupplyChainTransaction).filter(models.SupplyChainTransaction.transaction_id == transaction_id).first()

def get_supply_chain_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SupplyChainTransaction).offset(skip).limit(limit).all()

def get_supply_chain_transactions_by_crop(db: Session, crop_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SupplyChainTransaction).filter(models.SupplyChainTransaction.crop_id == crop_id).offset(skip).limit(limit).all()

def create_supply_chain_transaction(db: Session, transaction: schemas.SupplyChainTransactionCreate):
    db_transaction = models.SupplyChainTransaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_supply_chain_transaction(db: Session, transaction_id: int, transaction: schemas.SupplyChainTransactionCreate):
    db_transaction = get_supply_chain_transaction(db, transaction_id)
    if db_transaction:
        for key, value in transaction.model_dump().items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_supply_chain_transaction(db: Session, transaction_id: int):
    db_transaction = get_supply_chain_transaction(db, transaction_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction