### Minimal import for a Streamlit page ###
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

### Initialize Supabase client ###
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

### Functions for the page ###
@st.dialog("Editar solicitud", width="large")
def update_request_form(id:int, request_category_default:list, measure_type_default: str, estimated_amount_default: int, details_default: str):
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
            options=get_enum_values("residue_type"),
            default=request_category_default
        )
        col1,col2 = st.columns(2)
        with col1:
            measure_type = st.radio("Tipo de unidades", options=["m3", "kg"], index=["m3", "kg"].index(measure_type_default))
        with col2:
            estimated_amount = st.number_input("Cantidad estimada", min_value=1, step=1, value=estimated_amount_default)
        details = st.text_area("Comentarios", value=details_default)
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            update_request(id, request_category, measure_type, estimated_amount, details)           

def update_request(request_id: int, request_category:list, measure_type: str, estimated_amount: int,details: str):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    print(now)
    try:
        request = supabase.table("requests").update({
            "request_category": request_category,
            "measure_type": measure_type,
            "estimated_amount": estimated_amount,
            "details": details,
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
            "request_category, measure_type, estimated_amount, details"
        ).eq("id", request_id).execute()
        return request.data[0] if request.data else None
    except Exception as e:
        st.error(f"Error fetching request: {e}")
        return None

def delete_request(ids: list):
    try:
        for request_id in ids:
            supabase.table("requests").delete().eq("id", request_id).execute()
        return st.toast("✅ Solicitud(es) eliminada(s) exitosamente")
    except Exception as e:
        return st.toast(f"❌ Error al eliminar la(s) solicitud(es): {e}")

def create_request_button():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Crear nueva solicitud", width="stretch"):
            create_request_form() 

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching enum values: {e}")

def create_request(username: str, request_category:list, measure_type: str, estimated_amount: int,details: str):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    print(now)
    try:
        request = supabase.table("requests").insert({
            "username": username,
            "service_type": "Recolección",
            "request_category": request_category,
            "measure_type": measure_type,
            "estimated_amount": estimated_amount,
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
            "id, username, service_type, request_category, measure_type, estimated_amount, details, status, admin_note, created_at, updated_at, assigned_provider, pickup_date"
        ).order("id", desc=True).limit(limit).execute()
        return requests.data
    except Exception as e:
        st.error(f"Error fetching requests: {e}")
        return []

@st.dialog("Crear solicitud", width="large")
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
            options=get_enum_values("residue_type")
        )
        col1,col2 = st.columns(2)
        with col1:
            measure_type = st.radio("Tipo de unidades", options=["m3", "kg"])
        with col2:
            estimated_amount = st.number_input("Cantidad estimada", min_value=1, max_value=100, step=1)
        details = st.text_area("Comentarios")
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            username = "user1"
            try:        
                create_request(username, request_category, measure_type, estimated_amount, details)
                st.toast("✅ Solicitud creada exitosamente")
                st.rerun()
            except Exception as e:
                st.toast(f"❌ Error al crear la solicitud")

def display_pending_requests_table(requests_data):
    try:   
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]
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
                if st.button("🔁 Editar solicitud", width="stretch"):
                    default_options = select_request(displayed_table[displayed_table["Seleccionar"]].index.tolist()[0])
                    update_request_form(
                        id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0],
                        request_category_default=default_options["request_category"],
                        measure_type_default=default_options["measure_type"],
                        estimated_amount_default=default_options["estimated_amount"],
                        details_default=default_options["details"]
                    )
        if selected_count > 0 or selected_count >= 2:
            with col2:
                if st.button("🗑️ Eliminar solicitudes", width="stretch"):
                    confirm_delete_dialog(displayed_table[displayed_table["Seleccionar"]].index.tolist())
           
    except Exception as e:
            st.write(f"No hay solicitudes pendientes disponibles") 

def display_all_requests_table(requests_data):
    try:
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","status", "request_category","measure_type","estimated_amount", "assigned_provider", "pickup_date", "admin_note","created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)

        st.dataframe(
            rows,
            width="stretch",
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
    except Exception as e:
        st.write(f"No hay solicitudes disponibles")

@st.dialog("⚠️ Confirmar eliminación")
def confirm_delete_dialog(request_ids: list):
    """Confirmation dialog for deleting requests."""
    st.warning(f"¿Estás seguro de que deseas eliminar {len(request_ids)} solicitud(es)?")
    st.markdown("Esta acción eliminará:")
    st.markdown("- Los registros de la base de datos")
    st.error("⚠️ Esta acción no se puede deshacer.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancelar", width="stretch", type="secondary"):
            st.rerun()
    with col2:
        if st.button("🗑️ Eliminar", width="stretch", type="primary"):
            if delete_request(request_ids):
                time.sleep(1)
                st.rerun()

### Page layout and logic ###
if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:

    ### Navigation template ###

    ### Formulario de solicitud de servicio ###
    st.page_link("./pages/nav4.py", label="⬅️ Atrás", use_container_width=True)
    mc.logout_and_home()

    st.subheader("📋 Solicitud de servicio")

    create_request_button()

    st.divider()
    tab1, tab2 = st.tabs(["📄 Solicitudes pendientes", "📊 Todas las solicitudes"])
    with tab1:
        display_pending_requests_table(list_all_requests())
    with tab2:
        display_all_requests_table(list_all_requests())

else:
    st.switch_page("./pages/login_home.py")
