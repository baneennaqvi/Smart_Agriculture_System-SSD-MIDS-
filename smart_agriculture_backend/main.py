from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

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
