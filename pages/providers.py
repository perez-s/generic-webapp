### Minimal import for a Streamlit page ###
import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import modules.common as mc

### Page specific imports ###
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
def create_provider(
        username: str,
        provider_name: str, 
        provider_nit: int, 
        provider_email: str, 
        provider_contact: str, 
        provider_contact_phone: int, 
        provider_category: list,
        provider_activity: list, 
        lic_amb_path: str, 
        rut_path: str, 
        ccio_path: str, 
        other_docs_path: str
    ):
    now = datetime.now(timezone(timedelta(hours=5))).isoformat()
    print(now)
    try:
        request = supabase.table("providers").insert({
            "username": username,
            "provider_name": provider_name,
            "provider_nit": provider_nit,
            "provider_email": provider_email,
            "provider_contact": provider_contact,
            "provider_contact_phone": provider_contact_phone,
            "provider_category": provider_category,
            "provider_activity": provider_activity,
            "lic_amb_path": lic_amb_path,
            "rut_path": rut_path,
            "ccio_path": ccio_path,
            "other_docs_path": other_docs_path,
            "created_at": now,
            "updated_at": now
        }).execute()
        return request

    except Exception as e:
        st.error(f"Error creando proveedor: {e}")

def list_all_providers(limit=200):
    try:
        providers = supabase.table("providers").select(
            "id, username, provider_name, provider_category, lic_amb_path, rut_path, ccio_path, other_docs_path, created_at, updated_at"
        ).order("id", desc=True).limit(limit).execute()
        return providers.data
    except Exception as e:
        st.error(f"Error fetching providers: {e}")
        return []

def format_date(date_str: str) -> str:
    # When displaying dates from Supabase, parse and format them
    # Parse ISO format string to datetime
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    # Format as desired
    return date_obj.strftime("%Y %B  %d %H:%M %Z")

def path_file(provider_nit, provider_name, file_name, upload_file) -> str:
    return f"uploads/{provider_nit}_{provider_name}_{file_name}.{upload_file.type.split('/')[-1]}"

def save_file(file_uploader, file_path) -> str:
    with open(file_path, mode='wb') as w:
        w.write(file_uploader.getvalue())
    return file_path

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching enum values: {e}")

@st.dialog("Crear proveedor")
def create_provider_dialog():
    providers_form = st.form("providers_form")
    with providers_form:
        with st.expander("Instrucciones"):
            st.markdown(
                """ 
                - Ingresa el nombre del proveedor.
                - Sube los documentos requeridos.
                - Presiona el botón para crear el proveedor.
                """
            )
        provider_name = st.text_input("Nombre del proveedor")
        provider_nit = st.number_input("NIT del proveedor", step=1, format="%d")
        provider_email = st.text_input("Correo electrónico del proveedor")
        provider_contact = st.text_input("Contacto")
        provider_contact_phone = st.text_input("Teléfono")
        provider_category = st.multiselect(
            "Tipos de residuos",
            options=get_enum_values("residue_type")
        )
        provider_auth_activities = st.multiselect(
            "Actividades autorizadas",
            options=get_enum_values("activities_performed")
        )
        lic_amb_file = st.file_uploader("Licencia ambiental", type=["pdf", "jpg", "png"])
        rut_file = st.file_uploader("RUT", type=["pdf", "jpg", "png"])
        ccio_file = st.file_uploader("Cámara de comercio", type=["pdf", "jpg", "png"])
        other_docs_file = st.file_uploader("Otros documentos", type=["pdf", "jpg", "png"])    
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            username = "user1"
            lic_amb_path = path_file(provider_nit, provider_name, "lic_amb", lic_amb_file)
            rut_path = path_file(provider_nit, provider_name, "rut", rut_file)
            ccio_path = path_file(provider_nit, provider_name, "ccio", ccio_file)
            other_docs_path = path_file(provider_nit, provider_name, "other_docs", other_docs_file)
            create_provider(username, provider_name, provider_nit, provider_email, provider_contact, provider_contact_phone, provider_category, provider_auth_activities, lic_amb_path, rut_path, ccio_path, other_docs_path)
            save_file(lic_amb_file, lic_amb_path)
            save_file(rut_file, rut_path)
            save_file(ccio_file, ccio_path)
            save_file(other_docs_file, other_docs_path)
            st.toast("✅ Proveedor creado exitosamente! ")
            time.sleep(2)
            st.rerun()

def display_providers_table(providers_data):
    try:
        rows = pd.DataFrame(providers_data)
        rows = rows[["id", "provider_name","provider_category", "created_at", "updated_at"]]
        rows.set_index("id", inplace=True)
        st.dataframe(
            rows,
            width="stretch",
            column_config={
                "id": "ID del proveedor",
                "provider_name": "Nombre del proveedor",
                "created_at": st.column_config.DateColumn(
                    "Creado en",
                    format="D/M/Y H:M"
                ),
                "updated_at": st.column_config.DateColumn(
                    "Actualizado en",
                    format="D/M/Y H:M"
                )
            }
        )
    except Exception as e:
        st.write(f"No hay datos disponibles") 

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
mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:
    get_enum_values("residue_type")
    columns = st.columns(6)
    with columns[0]:
        st.page_link("./pages/login_home.py", label="🏠 Inicio", use_container_width=True)
        authenticator.logout(button_name='Cerrar sesión', location='main', use_container_width=True, key='logoutformats')
    with columns[5]:
        st.image("./resources/Logo2.png", width=10, use_container_width=True)
    ### Formulario de solicitud de servicio ###
    st.subheader("📋 Creación de proveedor")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Crear nuevo proveedor", width="stretch"):
            create_provider_dialog()
    with col2:
        if st.button("🔁 Actualizar proveedor", width="stretch"):
            st.toast("🚧 Funcionalidad en desarrollo")

    with col3:
        if st.button("❌ Eliminar proveedor", width="stretch"):
            st.toast("🚧 Funcionalidad en desarrollo")


    st.divider()

    st.subheader("📋 Lista de proveedores")

    display_providers_table(list_all_providers(200))


else:
    st.switch_page("./pages/login_home.py")