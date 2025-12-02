import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import modules.common as mc

### Page specific imports ###
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import locale
import pandas as pd

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Cargar variables de entorno y configurar Supabase
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_providers():
    try:
        providers = supabase.table("providers").select("provider_name").execute()
        return [provider['provider_name'] for provider in providers.data]
    except Exception as e:
        st.error(f"Error fetching providers: {e}")
        return []

def display_pending_requests_table(requests_data):
    try:   
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","username","status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]
        rows = rows[rows["status"] == "Pendiente"]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False

        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","status", "request_category", "measure_type", "estimated_amount", "created_at", "updated_at"], 
            column_config={
                "id": "ID",
                "request_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_type"),
                    color=["blue", "green", "orange", "red", "purple", "brown", "gray"]
                ),
                "measure_type": "Tipo de unidad",
                "estimated_amount": "Cantidad estimada",
                "status": st.column_config.MultiselectColumn(
                    "Estado",
                    options=get_enum_values("status_type"),
                    color=["blue", "green", "red"]
                ),
                "created_at": st.column_config.DateColumn(
                    "Fecha de creación",
                    format="DD/MM/YY HH:mm"
                ),
                "updated_at": st.column_config.DateColumn(
                    "Última modificación",
                    format="DD/MM/YY HH:mm"
                )
            }
        )
        selected_count = displayed_table.Seleccionar.sum()
        col1, col2 = st.columns(2)
        if selected_count > 0 and selected_count < 2:
            with col1:    
                if st.button("🔁 Responder solicitud", width="stretch"):
                    default_options = select_request(displayed_table[displayed_table["Seleccionar"]].index.tolist()[0])
                    answer_request_form(
                        id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0],
                        username=default_options["username"],
                        status=default_options["status"],
                        request_category_default=default_options["request_category"],
                        measure_type_default=default_options["measure_type"],
                        estimated_amount_default=default_options["estimated_amount"],
                        details_default=default_options["details"],
                        admin_note_default=default_options["admin_note"],
                        pickup_date_default=default_options["pickup_date"],
                        assigned_provider_default=default_options["assigned_provider"]
                    )
        if selected_count >= 2:
            with col1:
                if st.button("🔁 Editar solicitud", width="stretch"):
                    st.toast("❌ Selecciona solo una solicitud para editar")
    except Exception as e:
            st.write(f"No hay solicitudes pendientes disponibles") 

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching enum values: {e}")

@st.dialog("Responder solicitud", width="large")
def answer_request_form(id:int, username:str, status:str, request_category_default:list, measure_type_default: str, estimated_amount_default: int, details_default: str, admin_note_default: str, pickup_date_default: str, assigned_provider_default: str):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    request_form = st.form("request_form")
    with request_form:
        st.write(f"### Responder solicitud ID: {id} del usuario: {username}")
        request_category = st.multiselect(
            "Categoria de los residuos",
            options=get_enum_values("residue_type"),
            default=request_category_default,
            disabled=True
        )
        col1,col2 = st.columns(2)
        with col1:
            measure_type = st.radio("Tipo de unidades", options=["m3", "kg"], index=["m3", "kg"].index(measure_type_default), disabled=True)
        with col2:
            estimated_amount = st.number_input("Cantidad estimada", min_value=1, max_value=100, step=1, value=estimated_amount_default, disabled=True)
        details = st.text_area("Comentarios", value=details_default, disabled=True)
        st.divider()
        cols = st.columns(2)
        with cols[0]:
            request_status = st.selectbox("Estado de la solicitud", options=get_enum_values("status_type"), index=get_enum_values("status_type").index(status), disabled=False)
            pickup_date = st.date_input("Fecha de recolección estimada", min_value="today", format="DD/MM/YYYY", value=pickup_date_default)
        with cols[1]:
            providers_list = get_providers()
            default_index = providers_list.index(assigned_provider_default) if assigned_provider_default in providers_list else None
            provider_assigned = st.selectbox("Asignar proveedor", options=providers_list, index=default_index, disabled=False)
        admin_note = st.text_area("Nota para el usuario (opcional)", value=admin_note_default)
        submitted = st.form_submit_button("Responder solicitud")
        if submitted:
            update_request(id, request_status, pickup_date.isoformat(), provider_assigned, admin_note)         

def update_request(request_id: int, request_status: str, pickup_date: str, provider_assigned: str, admin_note: str):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    print(now)
    try:
        request = supabase.table("requests").update({
            "status": request_status,
            "pickup_date": pickup_date,
            "assigned_provider": provider_assigned,
            "admin_note": admin_note,
            "updated_at": now
        }).eq("id", request_id).execute()
        st.toast("✅ Solicitud actualizada exitosamente")
        st.rerun()
        return request

    except Exception as e:
        st.error(f"Error updating request: {e}")

def select_request(request_id: int):
    try:
        request = supabase.table("requests").select(
            "username, status, request_category, measure_type, estimated_amount, details, admin_note, pickup_date, assigned_provider"
        ).eq("id", request_id).execute()
        return request.data[0] if request.data else None
    except Exception as e:
        st.error(f"Error fetching request: {e}")
        return None

def list_all_requests(limit=200):
    try:
        requests = supabase.table("requests").select(
            "id, username, service_type, request_category, measure_type, estimated_amount, details, status, assigned_provider, pickup_date, admin_note, created_at, updated_at"
        ).order("id", desc=True).limit(limit).execute()
        return requests.data
    except Exception as e:
        st.error(f"Error fetching requests: {e}")
        return []

def display_all_requests_table(requests_data):
    try:   
        rows = pd.DataFrame(requests_data)
        rows = rows[["id", "username","status", "request_category","measure_type","estimated_amount","assigned_provider","pickup_date","admin_note","created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows["pickup_date"] = pd.to_datetime(rows["pickup_date"])
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False

        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","status", "request_category","measure_type","estimated_amount","assigned_provider","pickup_date","admin_note","created_at", "updated_at"], 
            column_config={
                "id": "ID",
                "request_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_type"),
                    color=["blue", "green", "orange", "red", "purple", "brown", "gray"]
                ),
                "measure_type": "Tipo de unidad",
                "estimated_amount": "Cantidad estimada",
                "status": st.column_config.MultiselectColumn(
                    "Estado",
                    options=get_enum_values("status_type"),
                    color=["blue", "green", "red"]
                ),
                "assigned_provider": "Proveedor asignado",
                "pickup_date": st.column_config.DateColumn(
                    "Fecha de recogida",
                    format="DD/MM/YYYY"
                ),
                "admin_note": "Nota del administrador",
                "created_at": st.column_config.DateColumn(
                    "Fecha de creación",
                    format="DD/MM/YY HH:mm"
                ),
                "updated_at": st.column_config.DateColumn(
                    "Última modificación",
                    format="DD/MM/YY HH:mm"
                )
            }
        )
        selected_count = displayed_table.Seleccionar.sum()
        col1, col2 = st.columns(2)
        if selected_count > 0 and selected_count < 2:
            with col1:    
                if st.button("🔁 Responder solicitud", width="stretch"):
                    default_options = select_request(displayed_table[displayed_table["Seleccionar"]].index.tolist()[0])
                    answer_request_form(
                        id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0],
                        username=default_options["username"],
                        status=default_options["status"],
                        request_category_default=default_options["request_category"],
                        measure_type_default=default_options["measure_type"],
                        estimated_amount_default=default_options["estimated_amount"],
                        details_default=default_options["details"],
                        admin_note_default=default_options["admin_note"],
                        pickup_date_default=default_options["pickup_date"],
                        assigned_provider_default=default_options["assigned_provider"]
                    )
        if selected_count >= 2:
            with col1:
                if st.button("🔁 Editar solicitud", width="stretch"):
                    st.toast("❌ Selecciona solo una solicitud para editar")
    except Exception as e:
            st.write(f"No hay solicitudes pendientes disponibles {e}") 


if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:

    ### Navigation template ###

    ### Formulario de solicitud de servicio ###
    st.page_link("./pages/nav4.py", label="⬅️ Atrás", use_container_width=True)
    mc.logout_and_home()

    tabs = st.tabs(["📄 Solicitudes pendientes", "📊 Todas las solicitudes"])
    with tabs[0]:
        display_pending_requests_table(list_all_requests())
    with tabs[1]:
        display_all_requests_table(list_all_requests())

else:
    st.switch_page("./pages/login_home.py")
