from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status

import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow CORS for frontend (like Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- USERS -----

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserBase, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user_update.name
    user.email = user_update.email
    user.role = user_update.role
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

# ----- SENSORS -----

@app.post("/sensors/", response_model=schemas.Sensor)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    return crud.create_sensor(db=db, sensor=sensor)

@app.get("/sensors/", response_model=list[schemas.Sensor])
def read_sensors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sensors(db, skip=skip, limit=limit)

@app.get("/sensors/{sensor_id}", response_model=schemas.Sensor)
def read_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = crud.get_sensor(db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor

@app.put("/sensors/{sensor_id}", response_model=schemas.Sensor)
def update_sensor(sensor_id: int, sensor_update: schemas.SensorCreate, db: Session = Depends(get_db)):
    sensor = crud.get_sensor(db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.type = sensor_update.type
    sensor.location = sensor_update.location
    sensor.status = sensor_update.status
    db.commit()
    db.refresh(sensor)
    return sensor

@app.delete("/sensors/{sensor_id}")
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = crud.get_sensor(db, sensor_id=sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    db.delete(sensor)
    db.commit()
    return {"message": "Sensor deleted successfully"}


# ----- SENSOR DATA -----

@app.post("/sensor-data/", response_model=schemas.SensorData)
def create_sensor_data(sensor_data: schemas.SensorDataCreate, db: Session = Depends(get_db)):
    return crud.create_sensor_data(db=db, sensor_data=sensor_data)

@app.get("/sensor-data/", response_model=list[schemas.SensorData])
def get_all_sensor_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_sensor_data(db, skip=skip, limit=limit)

@app.get("/sensor-data/{data_id}", response_model=schemas.SensorData)
def get_sensor_data_by_id(data_id: int, db: Session = Depends(get_db)):
    data = crud.get_sensor_data(db, data_id=data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return data

@app.get("/sensor-data/by-sensor/{sensor_id}", response_model=list[schemas.SensorData])
def get_data_by_sensor(sensor_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sensor_data_by_sensor(db, sensor_id=sensor_id, skip=skip, limit=limit)

@app.put("/sensor-data/{data_id}", response_model=schemas.SensorData)
def update_sensor_data(data_id: int, sensor_data: schemas.SensorDataCreate, db: Session = Depends(get_db)):
    data = crud.update_sensor_data(db, data_id=data_id, sensor_data=sensor_data)
    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return data

@app.delete("/sensor-data/{data_id}")
def delete_sensor_data(data_id: int, db: Session = Depends(get_db)):
    data = crud.delete_sensor_data(db, data_id=data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return {"message": "Sensor data deleted successfully"}

# ----- IRRIGATION SYSTEMS -----

@app.post("/irrigation-systems/", response_model=schemas.IrrigationSystem)
def create_irrigation_system(irrigation: schemas.IrrigationSystemCreate, db: Session = Depends(get_db)):
    return crud.create_irrigation_system(db=db, irrigation=irrigation)

@app.get("/irrigation-systems/", response_model=list[schemas.IrrigationSystem])
def read_irrigation_systems(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_irrigation_systems(db, skip=skip, limit=limit)

@app.get("/irrigation-systems/{irrigation_id}", response_model=schemas.IrrigationSystem)
def read_irrigation_system(irrigation_id: int, db: Session = Depends(get_db)):
    irrigation = crud.get_irrigation_system(db, irrigation_id=irrigation_id)
    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation system not found")
    return irrigation

@app.get("/irrigation-systems/by-farm/{farm_id}", response_model=list[schemas.IrrigationSystem])
def read_irrigation_systems_by_farm(farm_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_irrigation_systems_by_farm(db, farm_id=farm_id, skip=skip, limit=limit)

@app.put("/irrigation-systems/{irrigation_id}", response_model=schemas.IrrigationSystem)
def update_irrigation_system(irrigation_id: int, irrigation_update: schemas.IrrigationSystemCreate, db: Session = Depends(get_db)):
    irrigation = crud.update_irrigation_system(db, irrigation_id=irrigation_id, irrigation=irrigation_update)
    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation system not found")
    return irrigation

@app.delete("/irrigation-systems/{irrigation_id}")
def delete_irrigation_system(irrigation_id: int, db: Session = Depends(get_db)):
    irrigation = crud.delete_irrigation_system(db, irrigation_id=irrigation_id)
    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation system not found")
    return {"message": "Irrigation system deleted successfully"}

# ----- WEATHER DATA -----

@app.post("/weather-data/", response_model=schemas.WeatherData)
def create_weather_data(weather: schemas.WeatherDataCreate, db: Session = Depends(get_db)):
    return crud.create_weather_data(db=db, weather=weather)

@app.get("/weather-data/", response_model=list[schemas.WeatherData])
def read_weather_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_weather_data_list(db, skip=skip, limit=limit)

@app.get("/weather-data/{weather_id}", response_model=schemas.WeatherData)
def read_weather_data_by_id(weather_id: int, db: Session = Depends(get_db)):
    weather = crud.get_weather_data(db, weather_id=weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return weather

@app.put("/weather-data/{weather_id}", response_model=schemas.WeatherData)
def update_weather_data(weather_id: int, weather_update: schemas.WeatherDataCreate, db: Session = Depends(get_db)):
    weather = crud.update_weather_data(db, weather_id=weather_id, weather=weather_update)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return weather

@app.delete("/weather-data/{weather_id}")
def delete_weather_data(weather_id: int, db: Session = Depends(get_db)):
    weather = crud.delete_weather_data(db, weather_id=weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return {"message": "Weather data deleted successfully"}

# ----- CROP MANAGEMENT -----

@app.post("/crops/", response_model=schemas.CropManagement)
def create_crop(crop: schemas.CropManagementCreate, db: Session = Depends(get_db)):
    return crud.create_crop(db=db, crop=crop)

@app.get("/crops/", response_model=list[schemas.CropManagement])
def read_crops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_crops(db, skip=skip, limit=limit)

@app.get("/crops/{crop_id}", response_model=schemas.CropManagement)
def read_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = crud.get_crop(db, crop_id=crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop

@app.put("/crops/{crop_id}", response_model=schemas.CropManagement)
def update_crop(crop_id: int, crop_update: schemas.CropManagementCreate, db: Session = Depends(get_db)):
    crop = crud.update_crop(db, crop_id=crop_id, crop=crop_update)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop

@app.delete("/crops/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = crud.delete_crop(db, crop_id=crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return {"message": "Crop deleted successfully"}

# ----- FERTILIZATION SYSTEMS -----

@app.post("/fertilization-systems/", response_model=schemas.FertilizationSystem)
def create_fertilization_system(fertilization: schemas.FertilizationSystemCreate, db: Session = Depends(get_db)):
    return crud.create_fertilization_system(db=db, fertilization=fertilization)

@app.get("/fertilization-systems/", response_model=list[schemas.FertilizationSystem])
def read_fertilization_systems(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_fertilization_systems(db, skip=skip, limit=limit)

@app.get("/fertilization-systems/{fertilization_id}", response_model=schemas.FertilizationSystem)
def read_fertilization_system(fertilization_id: int, db: Session = Depends(get_db)):
    fertilization = crud.get_fertilization_system(db, fertilization_id=fertilization_id)
    if not fertilization:
        raise HTTPException(status_code=404, detail="Fertilization system not found")
    return fertilization

@app.get("/fertilization-systems/by-farm/{farm_id}", response_model=list[schemas.FertilizationSystem])
def read_fertilization_systems_by_farm(farm_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_fertilization_systems_by_farm(db, farm_id=farm_id, skip=skip, limit=limit)

@app.put("/fertilization-systems/{fertilization_id}", response_model=schemas.FertilizationSystem)
def update_fertilization_system(fertilization_id: int, fertilization_update: schemas.FertilizationSystemCreate, db: Session = Depends(get_db)):
    fertilization = crud.update_fertilization_system(db, fertilization_id=fertilization_id, fertilization=fertilization_update)
    if not fertilization:
        raise HTTPException(status_code=404, detail="Fertilization system not found")
    return fertilization

@app.delete("/fertilization-systems/{fertilization_id}")
def delete_fertilization_system(fertilization_id: int, db: Session = Depends(get_db)):
    fertilization = crud.delete_fertilization_system(db, fertilization_id=fertilization_id)
    if not fertilization:
        raise HTTPException(status_code=404, detail="Fertilization system not found")
    return {"message": "Fertilization system deleted successfully"}

# ----- PEST & DISEASE DETECTION -----

@app.post("/pest-disease-detections/", response_model=schemas.PestDiseaseDetection)
def create_pest_disease_detection(detection: schemas.PestDiseaseDetectionCreate, db: Session = Depends(get_db)):
    return crud.create_pest_disease_detection(db=db, detection=detection)

@app.get("/pest-disease-detections/", response_model=list[schemas.PestDiseaseDetection])
def read_pest_disease_detections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pest_disease_detections(db, skip=skip, limit=limit)

@app.get("/pest-disease-detections/{detection_id}", response_model=schemas.PestDiseaseDetection)
def read_pest_disease_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = crud.get_pest_disease_detection(db, detection_id=detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Pest & disease detection not found")
    return detection

@app.get("/pest-disease-detections/by-crop/{crop_id}", response_model=list[schemas.PestDiseaseDetection])
def read_pest_disease_detections_by_crop(crop_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pest_disease_detections_by_crop(db, crop_id=crop_id, skip=skip, limit=limit)

@app.put("/pest-disease-detections/{detection_id}", response_model=schemas.PestDiseaseDetection)
def update_pest_disease_detection(detection_id: int, detection_update: schemas.PestDiseaseDetectionCreate, db: Session = Depends(get_db)):
    detection = crud.update_pest_disease_detection(db, detection_id=detection_id, detection=detection_update)
    if not detection:
        raise HTTPException(status_code=404, detail="Pest & disease detection not found")
    return detection

@app.delete("/pest-disease-detections/{detection_id}")
def delete_pest_disease_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = crud.delete_pest_disease_detection(db, detection_id=detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Pest & disease detection not found")
    return {"message": "Pest & disease detection deleted successfully"}

# ----- SUPPLY CHAIN TRANSACTIONS -----

@app.post("/supply-chain-transactions/", response_model=schemas.SupplyChainTransaction)
def create_supply_chain_transaction(transaction: schemas.SupplyChainTransactionCreate, db: Session = Depends(get_db)):
    return crud.create_supply_chain_transaction(db=db, transaction=transaction)

@app.get("/supply-chain-transactions/", response_model=list[schemas.SupplyChainTransaction])
def read_supply_chain_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_supply_chain_transactions(db, skip=skip, limit=limit)

@app.get("/supply-chain-transactions/{transaction_id}", response_model=schemas.SupplyChainTransaction)
def read_supply_chain_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_supply_chain_transaction(db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Supply chain transaction not found")
    return transaction

@app.get("/supply-chain-transactions/by-crop/{crop_id}", response_model=list[schemas.SupplyChainTransaction])
def read_supply_chain_transactions_by_crop(crop_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_supply_chain_transactions_by_crop(db, crop_id=crop_id, skip=skip, limit=limit)

@app.put("/supply-chain-transactions/{transaction_id}", response_model=schemas.SupplyChainTransaction)
def update_supply_chain_transaction(transaction_id: int, transaction_update: schemas.SupplyChainTransactionCreate, db: Session = Depends(get_db)):
    transaction = crud.update_supply_chain_transaction(db, transaction_id=transaction_id, transaction=transaction_update)
    if not transaction:
        raise HTTPException(status_code=404, detail="Supply chain transaction not found")
    return transaction

@app.delete("/supply-chain-transactions/{transaction_id}")
def delete_supply_chain_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.delete_supply_chain_transaction(db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Supply chain transaction not found")
    return {"message": "Supply chain transaction deleted successfully"}

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta=None):
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import APIRouter
from fastapi import Security
from fastapi import HTTPException, Depends

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
