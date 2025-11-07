### Minimal import for a Streamlit page ###
import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

### Page specific imports ###
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import locale
import pandas as pd
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

### Initialize Supabase client ###
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

### Functions for the page ###
def create_request(username: str, request_category:list, estimated_weight_kg: int,details: str):
    now = datetime.now(timezone(timedelta(hours=5))).isoformat()
    print(now)
    try:
        request = supabase.table("requests").insert({
            "username": username,
            "service_type": "Recolección",
            "request_category": request_category,
            "estimated_weight_kg": estimated_weight_kg,
            "details": details,
            "status": "Pendiente",
            "admin_note": "",
            "created_at": now,
            "updated_at": now
        }).execute()
        return request

    except Exception as e:
        st.error(f"Error creating request: {e}")

def list_all_requests(limit=200):
    try:
        requests = supabase.table("requests").select(
            "id, username, service_type, request_category, estimated_weight_kg, details, status, admin_note, created_at, updated_at"
        ).order("id", desc=True).limit(limit).execute()
        return requests.data
    except Exception as e:
        st.error(f"Error fetching requests: {e}")
        return []

def format_date(date_str: str) -> str:
    # When displaying dates from Supabase, parse and format them
    # Parse ISO format string to datetime
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    # Format as desired
    return date_obj.strftime("%Y %B  %d %H:%M %Z")

def create_request_form():
    request_form = st.form("request_form")
    with request_form:
        with st.expander("Instrucciones"):
            st.markdown(
                """
                - Selecciona el tipo de servicio que necesitas.
                - Ingresa el volumen estimado (m³). Debe estar entre 0.1 m³ y 100 m³.
                - Proporciona cualquier detalle adicional o comentario relevante.
                - Haz clic en 'Enviar solicitud' para completar el proceso.
                """
            )
        request_category = st.multiselect(
            "Categoria de los residuos",
            options=[
                "Aceites usados",
                "Pilas y baterias",
                "Luminarias",
                "Biosanitarios",
                "RAEE",
                "Pinturas",
                "Otros peligrosos"
            ]
        )
        stimated_weight_kg = st.number_input("Volumen estimado (m³)", min_value=1, max_value=100, step=1)
        details = st.text_area("Comentarios")
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            username = "user1"
            create_request(username, request_category, stimated_weight_kg, details)
            st.success("Request submitted successfully!")

def display_requests_table(requests_data):
    rows = pd.DataFrame(requests_data)
    rows = rows[["id","status", "request_category","estimated_weight_kg", "created_at", "updated_at"]]
    rows.set_index("id", inplace=True)
    st.dataframe(
        rows,
        width="stretch", 
        column_config={
            "id": "ID",
            "request_category": st.column_config.MultiselectColumn(
                "Categorías de residuos",
                options=[
                    "Aceites",
                    "Biosanitarios",
                    "RAEE y peligrosos",
                    "Pinturas"
                ],
                color=["blue", "green", "orange", "red"]
            ),
            "estimated_weight_kg": "Volumen estimado (m³)",
            "status": "Estado",
            "created_at": st.column_config.DateColumn(
                "Creado en",
                format="d/M/Y H:M"
            ),
            "updated_at": st.column_config.DateColumn(
                "Actualizado en",
                format="d/M/Y H:M"
            )
        }
    )

### Page layout and logic ###
authenticator = stauth.Authenticate('config.yaml')
CONFIG_FILENAME = 'config.yaml'
def get_roles():
    """Gets user roles based on config file."""
    with open(CONFIG_FILENAME) as file:
        config = yaml.load(file, Loader=SafeLoader)

    if config is not None:
        cred = config['credentials']
    else:
        cred = {}

    return {username: user_info['role'] for username, user_info in cred['usernames'].items() if 'role' in user_info}
if 'authentication_status' not in ss:
    st.switch_page('./pages/Inicio.py')

### Main page code ###
if ss["authentication_status"]:

    ### Navigation template ###

    ### Formulario de solicitud de servicio ###

    st.subheader("📋 Solicitud de servicio")
    
    create_request_form()

    st.divider()

    st.subheader("📄Estado de solicitudes de servicio")

    display_requests_table(list_all_requests())
else:
    st.switch_page("./pages/Inicio.py")
