import streamlit as st
import requests
from datetime import datetime

# Backend API URL
BACKEND_URL = "http://localhost:8000"  # Change if using Docker

# Helper function for API calls
def api_request(method, endpoint, data=None):
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data)
        elif method == "PUT":
            response = requests.put(f"{BACKEND_URL}{endpoint}", json=data)
        elif method == "DELETE":
            response = requests.delete(f"{BACKEND_URL}{endpoint}")
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# User Management Functions
def manage_users():
    st.header("👨‍🌾 User Management")
    
    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["View Users", "Add User", "Edit User", "Delete User"])
    
    with tab1:  # View Users
        if st.button("Load All Users"):
            users = api_request("GET", "/users/")
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
                    "role": role
                }
                result = api_request("POST", "/users/", user_data)
                if result:
                    st.success("User added successfully!")
    
    with tab3:  # Edit User
        users = api_request("GET", "/users/") or []
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
                        "role": new_role
                    }
                    result = api_request("PUT", f"/users/{user_id}", update_data)
                    if result:
                        st.success("User updated successfully!")
    
    with tab4:  # Delete User
        users = api_request("GET", "/users/") or []
        if users:
            user_options = {f"{u['user_id']} - {u['name']}": u['user_id'] for u in users}
            selected_user = st.selectbox("Select User to Delete", options=list(user_options.keys()))
            
            if st.button("Delete User"):
                user_id = user_options[selected_user]
                result = api_request("DELETE", f"/users/{user_id}")
                if result:
                    st.success("User deleted successfully!")

# Sensor Management Functions (similar structure)
def manage_sensors():
    st.header("📡 Sensor Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["View Sensors", "Add Sensor", "Edit Sensor", "Delete Sensor"])
    
    with tab1:  # View Sensors
        if st.button("Load All Sensors"):
            sensors = api_request("GET", "/sensors/")
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
                result = api_request("POST", "/sensors/", sensor_data)
                if result:
                    st.success("Sensor added successfully!")
    
    with tab3:  # Edit Sensor
        sensors = api_request("GET", "/sensors/") or []
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
                    result = api_request("PUT", f"/sensors/{sensor_id}", update_data)
                    if result:
                        st.success("Sensor updated successfully!")
    
    with tab4:  # Delete Sensor
        sensors = api_request("GET", "/sensors/") or []
        if sensors:
            sensor_options = {f"{s['sensor_id']} - {s['type']}": s['sensor_id'] for s in sensors}
            selected_sensor = st.selectbox("Select Sensor to Delete", options=list(sensor_options.keys()))
            
            if st.button("Delete Sensor"):
                sensor_id = sensor_options[selected_sensor]
                result = api_request("DELETE", f"/sensors/{sensor_id}")
                if result:
                    st.success("Sensor deleted successfully!")

# Main App
def main():
    st.title("🌱 Smart Agriculture System")
    
    menu = st.sidebar.selectbox("Menu", ["User Management", "Sensor Management"])
    
    if menu == "User Management":
        manage_users()
    elif menu == "Sensor Management":
        manage_sensors()

if __name__ == "__main__":
    main()