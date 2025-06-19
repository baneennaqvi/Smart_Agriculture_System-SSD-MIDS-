import streamlit as st
import requests
from datetime import datetime
import re

# Backend API URL
BACKEND_URL = "http://backend:8000"  # Using Docker service name

def api_request(method, endpoint, data=None, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(f"{BACKEND_URL}{endpoint}", json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(f"{BACKEND_URL}{endpoint}", headers=headers)
        if response.status_code in (200, 201):
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def login_form():
    st.title("🔒 Login or Register")
    auth_tab, reg_tab = st.tabs(["Login", "Register"])
    with auth_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    data = {"username": email, "password": password}
                    try:
                        response = requests.post(f"{BACKEND_URL}/login", data=data)
                        if response.status_code == 200:
                            token = response.json()["access_token"]
                            st.session_state["token"] = token
                            st.session_state["authenticated"] = True
                            st.success("Login successful!")
                        else:
                            st.error("Invalid credentials.")
                    except Exception as e:
                        st.error(f"Error: {e}")
    with reg_tab:
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email (register)")
            password = st.text_input("Password (min 8 chars)", type="password")
            role = st.selectbox("Role", ["farmer", "admin", "operator"])
            submit = st.form_submit_button("Register")
            if submit:
                if not name or not email or not password:
                    st.error("All fields are required.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif not re.match(r'^[a-zA-Z\s]+$', name):
                    st.error("Name must contain only alphabets and spaces.")
                else:
                    data = {"name": name, "email": email, "password": password, "role": role}
                    response = requests.post(f"{BACKEND_URL}/register", json=data)
                    if response.status_code == 200:
                        st.success("Registration successful! Please login.")
                    else:
                        try:
                            st.error(response.json().get("detail", "Registration failed."))
                        except:
                            st.error("Registration failed.")

def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        login_form()
        return
    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["token"] = None
        st.rerun()
    token = st.session_state.get("token")
    st.title("🌱 Smart Agriculture System")
    menu = st.sidebar.selectbox("Menu", [
        "User Management",
        "Sensor Management",
        "Sensor Data",
        "Irrigation Systems",
        "Weather Data",
        "Crop Management",
        "Pest & Disease Detection",
        "Supply Chain Transactions"
    ])
    if menu == "User Management":
        manage_users(token)
    elif menu == "Sensor Management":
        manage_sensors(token)
    elif menu == "Sensor Data":
        manage_sensor_data(token)
    elif menu == "Irrigation Systems":
        manage_irrigation(token)
    elif menu == "Weather Data":
        manage_weather(token)
    elif menu == "Crop Management":
        manage_crops(token)
    elif menu == "Pest & Disease Detection":
        manage_pest_disease(token)
    elif menu == "Supply Chain Transactions":
        manage_supply_chain(token)

def manage_users(token):
    st.header("👨‍🌾 User Management")
    
    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["View Users", "Add User", "Edit User", "Delete User"])
    
    with tab1:  # View Users
        if st.button("Load All Users"):
            users = api_request("GET", "/users/", token=token)
            if users:
                st.table(users)
    
    with tab2:  # Add User
        with st.form("add_user_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["farmer", "admin", "operator"])
            
            if st.form_submit_button("Add User"):
                user_data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "is_active": True
                }
                result = api_request("POST", "/users/", user_data, token=token)
                if result:
                    st.success("User added successfully!")
    
    with tab3:  # Edit User
        users = api_request("GET", "/users/", token=token) or []
        if users:
            user_options = {f"{u['user_id']} - {u['name']}": u['user_id'] for u in users}
            selected_user = st.selectbox("Select User to Edit", options=list(user_options.keys()))
            
            with st.form("edit_user_form"):
                user_id = user_options[selected_user]
                current_user = next(u for u in users if u['user_id'] == user_id)
                
                new_name = st.text_input("Name", value=current_user['name'])
                new_email = st.text_input("Email", value=current_user['email'])
                new_role = st.selectbox("Role", ["farmer", "admin", "operator"], 
                                      index=["farmer", "admin", "operator"].index(current_user['role']))
                
                if st.form_submit_button("Update User"):
                    update_data = {
                        "name": new_name,
                        "email": new_email,
                        "role": new_role,
                        "is_active": current_user.get('is_active', True)
                    }
                    result = api_request("PUT", f"/users/{user_id}", update_data, token=token)
                    if result:
                        st.success("User updated successfully!")
    
    with tab4:  # Delete User
        users = api_request("GET", "/users/", token=token) or []
        if users:
            user_options = {f"{u['user_id']} - {u['name']}": u['user_id'] for u in users}
            selected_user = st.selectbox("Select User to Delete", options=list(user_options.keys()))
            
            if st.button("Delete User"):
                user_id = user_options[selected_user]
                result = api_request("DELETE", f"/users/{user_id}", token=token)
                if result:
                    st.success("User deleted successfully!")

def manage_sensors(token):
    st.header("📡 Sensor Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Sensors", "Add Sensor", "Edit Sensor", "Delete Sensor"])
    
    with tab1:  # View Sensors
        if st.button("Load All Sensors"):
            sensors = api_request("GET", "/sensors/", token=token)
            if sensors:
                st.table(sensors)
    
    with tab2:  # Add Sensor
        with st.form("add_sensor_form"):
            sensor_type = st.selectbox("Type", ["temperature", "humidity", "soil_moisture", "pH"])
            location = st.text_input("Location")
            status = st.selectbox("Status", ["active", "inactive", "faulty"])
            
            if st.form_submit_button("Add Sensor"):
                sensor_data = {
                    "type": sensor_type,
                    "location": location,
                    "status": status
                }
                result = api_request("POST", "/sensors/", sensor_data, token=token)
                if result:
                    st.success("Sensor added successfully!")
    
    with tab3:  # Edit Sensor
        sensors = api_request("GET", "/sensors/", token=token) or []
        if sensors:
            sensor_options = {f"{s['sensor_id']} - {s['type']}": s['sensor_id'] for s in sensors}
            selected_sensor = st.selectbox("Select Sensor to Edit", options=list(sensor_options.keys()))
            
            with st.form("edit_sensor_form"):
                sensor_id = sensor_options[selected_sensor]
                current_sensor = next(s for s in sensors if s['sensor_id'] == sensor_id)
                
                new_type = st.selectbox("Type", ["temperature", "humidity", "soil_moisture", "pH"],
                                      index=["temperature", "humidity", "soil_moisture", "pH"].index(current_sensor['type']))
                new_location = st.text_input("Location", value=current_sensor['location'])
                new_status = st.selectbox("Status", ["active", "inactive", "faulty"],
                                        index=["active", "inactive", "faulty"].index(current_sensor['status']))
                
                if st.form_submit_button("Update Sensor"):
                    update_data = {
                        "type": new_type,
                        "location": new_location,
                        "status": new_status
                    }
                    result = api_request("PUT", f"/sensors/{sensor_id}", update_data, token=token)
                    if result:
                        st.success("Sensor updated successfully!")
    
    with tab4:  # Delete Sensor
        sensors = api_request("GET", "/sensors/", token=token) or []
        if sensors:
            sensor_options = {f"{s['sensor_id']} - {s['type']}": s['sensor_id'] for s in sensors}
            selected_sensor = st.selectbox("Select Sensor to Delete", options=list(sensor_options.keys()))
            
            if st.button("Delete Sensor"):
                sensor_id = sensor_options[selected_sensor]
                result = api_request("DELETE", f"/sensors/{sensor_id}", token=token)
                if result:
                    st.success("Sensor deleted successfully!")

def manage_sensor_data(token):
    st.header("📊 Sensor Data Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Sensor Data", "Add Sensor Data", "Edit Sensor Data", "Delete Sensor Data"])
    
    with tab1:  # View Sensor Data
        if st.button("Load All Sensor Data"):
            sensor_data = api_request("GET", "/sensor-data/", token=token)
            if sensor_data:
                st.table(sensor_data)
    
    with tab2:  # Add Sensor Data
        with st.form("add_sensor_data_form"):
            sensors = api_request("GET", "/sensors/", token=token) or []
            sensor_options = {f"{s['sensor_id']} - {s['type']}": s['sensor_id'] for s in sensors}
            sensor_id = st.selectbox("Select Sensor", options=list(sensor_options.keys()))
            
            temperature = st.number_input("Temperature (°C)", value=0.0)
            humidity = st.number_input("Humidity (%)", value=0.0)
            soil_moisture = st.number_input("Soil Moisture", value=0.0)
            ph_level = st.number_input("pH Level", value=0.0)
            
            if st.form_submit_button("Add Sensor Data"):
                data = {
                    "sensor_id": sensor_options[sensor_id],
                    "temperature": temperature,
                    "humidity": humidity,
                    "soil_moisture": soil_moisture,
                    "ph_level": ph_level
                }
                result = api_request("POST", "/sensor-data/", data, token=token)
                if result:
                    st.success("Sensor data added successfully!")

    with tab3:  # Edit Sensor Data
        sensor_data = api_request("GET", "/sensor-data/", token=token) or []
        if sensor_data:
            data_options = {f"{d['data_id']} - Sensor {d['sensor_id']}": d['data_id'] for d in sensor_data}
            selected_data = st.selectbox("Select Sensor Data to Edit", options=list(data_options.keys()))
            
            with st.form("edit_sensor_data_form"):
                data_id = data_options[selected_data]
                current_data = next(d for d in sensor_data if d['data_id'] == data_id)
                
                sensors = api_request("GET", "/sensors/", token=token) or []
                sensor_options = {f"{s['sensor_id']} - {s['type']}": s['sensor_id'] for s in sensors}
                
                # Get the current sensor type
                current_sensor = next((s for s in sensors if s['sensor_id'] == current_data['sensor_id']), None)
                current_sensor_key = f"{current_data['sensor_id']} - {current_sensor['type']}" if current_sensor else list(sensor_options.keys())[0]
                
                sensor_id = st.selectbox("Select Sensor", options=list(sensor_options.keys()),
                                       index=list(sensor_options.keys()).index(current_sensor_key) if current_sensor_key in sensor_options else 0)
                
                temperature = st.number_input("Temperature (°C)", value=current_data.get('temperature', 0.0) or 0.0)
                humidity = st.number_input("Humidity (%)", value=current_data.get('humidity', 0.0) or 0.0)
                soil_moisture = st.number_input("Soil Moisture", value=current_data.get('soil_moisture', 0.0) or 0.0)
                ph_level = st.number_input("pH Level", value=current_data.get('ph_level', 0.0) or 0.0)
                
                if st.form_submit_button("Update Sensor Data"):
                    update_data = {
                        "sensor_id": sensor_options[sensor_id],
                        "temperature": temperature,
                        "humidity": humidity,
                        "soil_moisture": soil_moisture,
                        "ph_level": ph_level
                    }
                    result = api_request("PUT", f"/sensor-data/{data_id}", update_data, token=token)
                    if result:
                        st.success("Sensor data updated successfully!")

    with tab4:  # Delete Sensor Data
        sensor_data = api_request("GET", "/sensor-data/", token=token) or []
        if sensor_data:
            data_options = {f"{d['data_id']} - Sensor {d['sensor_id']}": d['data_id'] for d in sensor_data}
            selected_data = st.selectbox("Select Sensor Data to Delete", options=list(data_options.keys()))
            
            if st.button("Delete Sensor Data"):
                data_id = data_options[selected_data]
                result = api_request("DELETE", f"/sensor-data/{data_id}", token=token)
                if result:
                    st.success("Sensor data deleted successfully!")

def manage_irrigation(token):
    st.title("Irrigation System Management")
    
    # Get all irrigation systems
    response = requests.get(f"{BACKEND_URL}/irrigation-systems", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        systems = response.json()
        
        # Create tabs for different operations
        tab1, tab2, tab3, tab4 = st.tabs(["View Systems", "Add System", "Edit System", "Delete System"])
        
        with tab1:
            st.subheader("View Irrigation Systems")
            if systems:
                for system in systems:
                    with st.expander(f"System {system['irrigation_id']}"):
                        st.write(f"**Farm ID:** {system['farm_id']}")
                        st.write(f"**Status:** {system['status']}")
                        st.write(f"**Water Usage:** {system['water_usage']} L")
                        st.write(f"**Last Activated:** {system['last_activated']}")
            else:
                st.info("No irrigation systems found")
        
        with tab2:
            st.subheader("Add New Irrigation System")
            with st.form("add_irrigation_system"):
                farm_id = st.number_input("Farm ID", min_value=1)
                status = st.selectbox("Status", ["on", "off"])
                water_usage = st.number_input("Water Usage (L)", min_value=0.0)
                
                if st.form_submit_button("Add System"):
                    system_data = {
                        "farm_id": farm_id,
                        "status": status,
                        "water_usage": water_usage
                    }
                    response = requests.post(f"{BACKEND_URL}/irrigation-systems", json=system_data, headers={"Authorization": f"Bearer {token}"})
                    if response.status_code == 200:
                        st.success("Irrigation system added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error adding irrigation system: {response.text}")
        
        with tab3:
            st.subheader("Edit Irrigation System")
            if systems:
                system_options = {f"System {s['irrigation_id']}": s for s in systems}
                selected_system = st.selectbox("Select System to Edit", list(system_options.keys()))
                current_system = system_options[selected_system]
                
                with st.form("edit_irrigation_system"):
                    new_farm_id = st.number_input("Farm ID", min_value=1, value=current_system['farm_id'])
                    new_status = st.selectbox("Status", ["on", "off"], 
                                            index=["on", "off"].index(current_system['status']))
                    new_water_usage = st.number_input("Water Usage (L)", min_value=0.0, 
                                                    value=float(current_system['water_usage']))
                    
                    if st.form_submit_button("Update System"):
                        system_data = {
                            "farm_id": new_farm_id,
                            "status": new_status,
                            "water_usage": new_water_usage
                        }
                        response = requests.put(f"{BACKEND_URL}/irrigation-systems/{current_system['irrigation_id']}", json=system_data, headers={"Authorization": f"Bearer {token}"})
                        if response.status_code == 200:
                            st.success("Irrigation system updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error updating irrigation system: {response.text}")
            else:
                st.info("No irrigation systems available to edit")
        
        with tab4:
            st.subheader("Delete Irrigation System")
            if systems:
                system_options = {f"System {s['irrigation_id']}": s for s in systems}
                selected_system = st.selectbox("Select System to Delete", list(system_options.keys()))
                current_system = system_options[selected_system]
                
                if st.button("Delete System"):
                    response = requests.delete(f"{BACKEND_URL}/irrigation-systems/{current_system['irrigation_id']}", headers={"Authorization": f"Bearer {token}"})
                    if response.status_code == 200:
                        st.success("Irrigation system deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error deleting irrigation system: {response.text}")
            else:
                st.info("No irrigation systems available to delete")
    else:
        st.error(f"Error fetching irrigation systems: {response.text}")

def manage_weather(token):
    st.header("🌤️ Weather Data Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Weather Data", "Add Weather Data", "Edit Weather Data", "Delete Weather Data"])
    
    with tab1:  # View Weather Data
        if st.button("Load All Weather Data"):
            weather_data = api_request("GET", "/weather-data/", token=token)
            if weather_data:
                st.table(weather_data)
    
    with tab2:  # Add Weather Data
        with st.form("add_weather_data_form"):
            temperature = st.number_input("Temperature (°C)", value=0.0)
            humidity = st.number_input("Humidity (%)", value=0.0)
            rainfall = st.number_input("Rainfall (mm)", value=0.0)
            wind_speed = st.number_input("Wind Speed (km/h)", value=0.0)
            
            if st.form_submit_button("Add Weather Data"):
                data = {
                    "temperature": temperature,
                    "humidity": humidity,
                    "rainfall": rainfall,
                    "wind_speed": wind_speed
                }
                result = api_request("POST", "/weather-data/", data, token=token)
                if result:
                    st.success("Weather data added successfully!")

    with tab3:  # Edit Weather Data
        weather_data = api_request("GET", "/weather-data/", token=token) or []
        if weather_data:
            data_options = {f"{d['weather_id']} - {d['timestamp']}": d['weather_id'] for d in weather_data}
            selected_data = st.selectbox("Select Weather Data to Edit", options=list(data_options.keys()))
            
            with st.form("edit_weather_data_form"):
                weather_id = data_options[selected_data]
                current_data = next(d for d in weather_data if d['weather_id'] == weather_id)
                
                temperature = st.number_input("Temperature (°C)", value=current_data['temperature'])
                humidity = st.number_input("Humidity (%)", value=current_data['humidity'])
                rainfall = st.number_input("Rainfall (mm)", value=current_data['rainfall'])
                wind_speed = st.number_input("Wind Speed (km/h)", value=current_data['wind_speed'])
                
                if st.form_submit_button("Update Weather Data"):
                    update_data = {
                        "temperature": temperature,
                        "humidity": humidity,
                        "rainfall": rainfall,
                        "wind_speed": wind_speed
                    }
                    result = api_request("PUT", f"/weather-data/{weather_id}", update_data, token=token)
                    if result:
                        st.success("Weather data updated successfully!")

    with tab4:  # Delete Weather Data
        weather_data = api_request("GET", "/weather-data/", token=token) or []
        if weather_data:
            data_options = {f"{d['weather_id']} - {d['timestamp']}": d['weather_id'] for d in weather_data}
            selected_data = st.selectbox("Select Weather Data to Delete", options=list(data_options.keys()))
            
            if st.button("Delete Weather Data"):
                weather_id = data_options[selected_data]
                result = api_request("DELETE", f"/weather-data/{weather_id}", token=token)
                if result:
                    st.success("Weather data deleted successfully!")

def manage_crops(token):
    st.header("🌾 Crop Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Crops", "Add Crop", "Edit Crop", "Delete Crop"])
    
    with tab1:  # View Crops
        crops = api_request("GET", "/crops/", token=token)
        if crops:
            st.table(crops)
        else:
            st.info("No crops found")
    
    with tab2:  # Add Crop
        with st.form("add_crop_form"):
            name = st.text_input("Crop Name (alphabets only)")
            planting_date = st.date_input("Planting Date")
            harvest_date = st.date_input("Expected Harvest Date", value=None)
            expected_yield = st.number_input("Expected Yield (kg)", min_value=0.0, step=0.1)
            status = st.selectbox("Status", ["planted", "growing", "ready_for_harvest", "harvested"])
            
            submit_button = st.form_submit_button("Add Crop")
            if submit_button:
                if not re.match(r'^[a-zA-Z\s]+$', name):
                    st.error("Crop name must contain only alphabets and spaces")
                else:
                    data = {
                        "name": name,
                        "planting_date": planting_date.isoformat(),
                        "harvest_date": harvest_date.isoformat() if harvest_date else None,
                        "expected_yield": expected_yield,
                        "status": status
                    }
                    result = api_request("POST", "/crops/", data, token=token)
                    if result:
                        st.success("Crop added successfully!")
                        st.rerun()
    
    with tab3:  # Edit Crop
        crops = api_request("GET", "/crops/", token=token)
        if not crops:
            st.info("No crops available to edit")
        else:
            crop_options = {f"{c['crop_id']} - {c['name']}": c['crop_id'] for c in crops}
            selected_crop = st.selectbox("Select Crop to Edit", options=list(crop_options.keys()))
            
            with st.form("edit_crop_form"):
                crop_id = crop_options[selected_crop]
                current_crop = next(c for c in crops if c['crop_id'] == crop_id)
                
                new_name = st.text_input("Crop Name (alphabets only)", value=current_crop['name'])
                new_planting_date = st.date_input("Planting Date", value=datetime.fromisoformat(current_crop['planting_date']).date())
                new_harvest_date = st.date_input("Expected Harvest Date", 
                                               value=datetime.fromisoformat(current_crop['harvest_date']).date() if current_crop['harvest_date'] else None)
                new_yield = st.number_input("Expected Yield (kg)", min_value=0.0, step=0.1, value=current_crop['expected_yield'])
                new_status = st.selectbox("Status", ["planted", "growing", "ready_for_harvest", "harvested"],
                                        index=["planted", "growing", "ready_for_harvest", "harvested"].index(current_crop['status']))
                
                submit_button = st.form_submit_button("Update Crop")
                if submit_button:
                    if not re.match(r'^[a-zA-Z\s]+$', new_name):
                        st.error("Crop name must contain only alphabets and spaces")
                    else:
                        update_data = {
                            "name": new_name,
                            "planting_date": new_planting_date.isoformat(),
                            "harvest_date": new_harvest_date.isoformat() if new_harvest_date else None,
                            "expected_yield": new_yield,
                            "status": new_status
                        }
                        result = api_request("PUT", f"/crops/{crop_id}", update_data, token=token)
                        if result:
                            st.success("Crop updated successfully!")
                            st.rerun()
    
    with tab4:  # Delete Crop
        crops = api_request("GET", "/crops/", token=token)
        if not crops:
            st.info("No crops available to delete")
        else:
            crop_options = {f"{c['crop_id']} - {c['name']}": c['crop_id'] for c in crops}
            selected_crop = st.selectbox("Select Crop to Delete", options=list(crop_options.keys()))
            
            if st.button("Delete Crop"):
                crop_id = crop_options[selected_crop]
                result = api_request("DELETE", f"/crops/{crop_id}", token=token)
                if result:
                    st.success("Crop deleted successfully!")
                    st.rerun()

def manage_pest_disease(token):
    st.header("🐛 Pest & Disease Detection")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Detections", "Add Detection", "Edit Detection", "Delete Detection"])
    
    with tab1:  # View Detections
        detections = api_request("GET", "/pest-disease-detections/", token=token)
        if detections:
            st.table(detections)
        else:
            st.info("No detections found")
    
    with tab2:  # Add Detection
        crops = api_request("GET", "/crops/", token=token)
        if not crops:
            st.warning("No crops available. Please add a crop first.")
        else:
            with st.form("add_detection_form"):
                crop_options = {f"{c['crop_id']} - {c['name']}": c['crop_id'] for c in crops}
                crop_id = st.selectbox("Select Crop", options=list(crop_options.keys()))
                
                symptom = st.text_area("Symptom Detected (minimum 10 characters)")
                diagnosis = st.text_area("Diagnosis (minimum 10 characters)")
                recommended_action = st.text_area("Recommended Action (minimum 10 characters)")
                
                submit_button = st.form_submit_button("Add Detection")
                if submit_button:
                    if len(symptom) < 10 or len(diagnosis) < 10 or len(recommended_action) < 10:
                        st.error("All text fields must be at least 10 characters long")
                    else:
                        data = {
                            "crop_id": crop_options[crop_id],
                            "symptom_detected": symptom,
                            "diagnosis": diagnosis,
                            "recommended_action": recommended_action
                        }
                        result = api_request("POST", "/pest-disease-detections/", data, token=token)
                        if result:
                            st.success("Detection added successfully!")
                            st.rerun()
    
    with tab3:  # Edit Detection
        detections = api_request("GET", "/pest-disease-detections/", token=token)
        if not detections:
            st.info("No detections available to edit")
        else:
            detection_options = {f"{d['detection_id']} - {d['symptom_detected']}": d['detection_id'] for d in detections}
            selected_detection = st.selectbox("Select Detection to Edit", options=list(detection_options.keys()))
            
            with st.form("edit_detection_form"):
                detection_id = detection_options[selected_detection]
                current_detection = next(d for d in detections if d['detection_id'] == detection_id)
                
                new_symptom = st.text_area("Symptom Detected (minimum 10 characters)", value=current_detection['symptom_detected'])
                new_diagnosis = st.text_area("Diagnosis (minimum 10 characters)", value=current_detection['diagnosis'])
                new_action = st.text_area("Recommended Action (minimum 10 characters)", value=current_detection['recommended_action'])
                
                submit_button = st.form_submit_button("Update Detection")
                if submit_button:
                    if len(new_symptom) < 10 or len(new_diagnosis) < 10 or len(new_action) < 10:
                        st.error("All text fields must be at least 10 characters long")
                    else:
                        update_data = {
                            "crop_id": current_detection['crop_id'],
                            "symptom_detected": new_symptom,
                            "diagnosis": new_diagnosis,
                            "recommended_action": new_action
                        }
                        result = api_request("PUT", f"/pest-disease-detections/{detection_id}", update_data, token=token)
                        if result:
                            st.success("Detection updated successfully!")
                            st.rerun()
    
    with tab4:  # Delete Detection
        detections = api_request("GET", "/pest-disease-detections/", token=token)
        if not detections:
            st.info("No detections available to delete")
        else:
            detection_options = {f"{d['detection_id']} - {d['symptom_detected']}": d['detection_id'] for d in detections}
            selected_detection = st.selectbox("Select Detection to Delete", options=list(detection_options.keys()))
            
            if st.button("Delete Detection"):
                detection_id = detection_options[selected_detection]
                result = api_request("DELETE", f"/pest-disease-detections/{detection_id}", token=token)
                if result:
                    st.success("Detection deleted successfully!")
                    st.rerun()

def manage_supply_chain(token):
    st.header("🔄 Supply Chain Transactions")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Transactions", "Add Transaction", "Edit Transaction", "Delete Transaction"])
    
    with tab1:  # View Transactions
        transactions = api_request("GET", "/supply-chain-transactions/", token=token)
        if transactions:
            st.table(transactions)
        else:
            st.info("No transactions found")
    
    with tab2:  # Add Transaction
        crops = api_request("GET", "/crops/", token=token)
        if not crops:
            st.warning("No crops available. Please add a crop first.")
        else:
            with st.form("add_transaction_form"):
                crop_options = {f"{c['crop_id']} - {c['name']}": c['crop_id'] for c in crops}
                crop_id = st.selectbox("Select Crop", options=list(crop_options.keys()))
                
                transaction_type = st.selectbox("Transaction Type", ["harvest", "transport", "storage", "sale", "purchase"])
                quantity = st.number_input("Quantity", min_value=0.1, step=0.1)
                price = st.number_input("Price", min_value=0.0, step=0.01)
                from_location = st.text_input("From Location (alphabets only)")
                to_location = st.text_input("To Location (alphabets only)")
                blockchain_hash = st.text_input("Blockchain Hash (10 alphanumeric characters)")
                status = st.selectbox("Status", ["pending", "completed", "failed"])
                
                submit_button = st.form_submit_button("Add Transaction")
                if submit_button:
                    if not re.match(r'^[a-zA-Z\s]+$', from_location) or not re.match(r'^[a-zA-Z\s]+$', to_location):
                        st.error("Locations must contain only alphabets and spaces")
                    elif not re.match(r'^[a-zA-Z0-9]{10}$', blockchain_hash):
                        st.error("Blockchain hash must be exactly 10 alphanumeric characters (letters and numbers only)")
                    else:
                        data = {
                            "crop_id": crop_options[crop_id],
                            "transaction_type": transaction_type,
                            "quantity": quantity,
                            "price": price,
                            "from_location": from_location,
                            "to_location": to_location,
                            "blockchain_hash": blockchain_hash,
                            "status": status
                        }
                        result = api_request("POST", "/supply-chain-transactions/", data, token=token)
                        if result:
                            st.success("Transaction added successfully!")
                            st.rerun()
    
    with tab3:  # Edit Transaction
        transactions = api_request("GET", "/supply-chain-transactions/", token=token)
        if not transactions:
            st.info("No transactions available to edit")
        else:
            transaction_options = {f"{t['transaction_id']} - {t['transaction_type']}": t['transaction_id'] for t in transactions}
            selected_transaction = st.selectbox("Select Transaction to Edit", options=list(transaction_options.keys()))
            
            with st.form("edit_transaction_form"):
                transaction_id = transaction_options[selected_transaction]
                current_transaction = next(t for t in transactions if t['transaction_id'] == transaction_id)
                
                new_type = st.selectbox("Transaction Type", ["harvest", "transport", "storage", "sale", "purchase"],
                                      index=["harvest", "transport", "storage", "sale", "purchase"].index(current_transaction['transaction_type']))
                new_quantity = st.number_input("Quantity", min_value=0.1, step=0.1, value=current_transaction['quantity'])
                new_price = st.number_input("Price", min_value=0.0, step=0.01, value=current_transaction['price'])
                new_from = st.text_input("From Location (alphabets only)", value=current_transaction['from_location'])
                new_to = st.text_input("To Location (alphabets only)", value=current_transaction['to_location'])
                new_hash = st.text_input("Blockchain Hash (10 alphanumeric characters)", value=current_transaction['blockchain_hash'])
                new_status = st.selectbox("Status", ["pending", "completed", "failed"], 
                                        index=["pending", "completed", "failed"].index(current_transaction['status']))
                
                submit_button = st.form_submit_button("Update Transaction")
                if submit_button:
                    if not re.match(r'^[a-zA-Z\s]+$', new_from) or not re.match(r'^[a-zA-Z\s]+$', new_to):
                        st.error("Locations must contain only alphabets and spaces")
                    elif not re.match(r'^[a-zA-Z0-9]{10}$', new_hash):
                        st.error("Blockchain hash must be exactly 10 alphanumeric characters (letters and numbers only)")
                    else:
                        update_data = {
                            "crop_id": current_transaction['crop_id'],
                            "transaction_type": new_type,
                            "quantity": new_quantity,
                            "price": new_price,
                            "from_location": new_from,
                            "to_location": new_to,
                            "blockchain_hash": new_hash,
                            "status": new_status
                        }
                        result = api_request("PUT", f"/supply-chain-transactions/{transaction_id}", update_data, token=token)
                        if result:
                            st.success("Transaction updated successfully!")
                            st.rerun()
    
    with tab4:  # Delete Transaction
        transactions = api_request("GET", "/supply-chain-transactions/", token=token)
        if not transactions:
            st.info("No transactions available to delete")
        else:
            transaction_options = {f"{t['transaction_id']} - {t['transaction_type']}": t['transaction_id'] for t in transactions}
            selected_transaction = st.selectbox("Select Transaction to Delete", options=list(transaction_options.keys()))
            
            if st.button("Delete Transaction"):
                transaction_id = transaction_options[selected_transaction]
                result = api_request("DELETE", f"/supply-chain-transactions/{transaction_id}", token=token)
                if result:
                    st.success("Transaction deleted successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()