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
        providers = supabase.table("providers").select("provider_name").eq("provider_is_active", True).execute()
        return [provider['provider_name'] for provider in providers.data]
    except Exception as e:
        st.error(f"Error fetching providers: {e.message}")
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

        if not rows.any().any():
            st.info("📭 No hay solicitudes pendientes aun.")
            return

        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","username","status", "request_category", "measure_type", "estimated_amount", "created_at", "updated_at"], 
            column_config={
                "id": "ID",
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    pinned=True
                ),
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
        if selected_count > 0:
            if st.button("🗓️ Agendar solicitud", width="stretch"):
                schedule_request_form(
                    ids=displayed_table[displayed_table["Seleccionar"]].index.tolist()
                )
    except Exception as e:
            st.write(f"No hay solicitudes pendientes disponibles") 

def display_all_requests_table(requests_data):
    try:   
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","username","status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)
        if not rows.any().any():
            st.info("📭 No hay solicitudes disponibles aun.")
            return

        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","username","status", "request_category", "measure_type", "estimated_amount", "created_at", "updated_at"], 
            column_config={
                "id": "ID",
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    pinned=True
                ),
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
    except Exception as e:
            st.write(f"No hay solicitudes pendientes disponibles") 

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching enum values: {e.message}")

@st.dialog("Programar solicitudes", width="large")
def schedule_request_form(ids: list):
    providers = get_providers()
    request_form = st.form("request_form")
    with request_form:
        cols = st.columns([1,2])
        with cols[0]:
            st.write(f"### Programación de recolección")
            pickup_date = st.date_input("Fecha de recolección")
            provider_name = st.selectbox("Proveedor asignado", options=providers)
            admin_note = st.text_area("Nota del administrador (opcional)")
            submitted = st.form_submit_button("Programar solicitud")
        with cols[1]:
            st.write("### Solicitudes seleccionadas:")
            df = pd.DataFrame(list_all_requests())
            df = df[df["id"].isin(ids)]
            df.set_index("id", inplace=True)
            st.dataframe(
                df[["username", "request_category", "measure_type", "estimated_amount"]],
                width="stretch",
                column_config={
                    "username": "Usuario",
                    "request_category": st.column_config.MultiselectColumn(
                        "Categorías de residuos",
                        options=get_enum_values("residue_type"),
                        color=["blue", "green", "orange", "red", "purple", "brown", "gray"]
                    ),
                    "measure_type": "Unidades",
                    "estimated_amount": "Cantidad estimada"
                }
                )

        if submitted:
            if admin_note == "":
                admin_note = None
            request = create_pickup(
                username=f"{ss["name"]}",
                provider_name=provider_name,
                pickup_date=pickup_date.isoformat(),
                admin_note=admin_note
            )
            create_pickup_requests(
                request_ids=ids,
                pickup_id=request.data[0]["id"]
            )
            update_request_status(
                request_ids=ids,
                request_status="Programada",
                admin_note=admin_note
            )

            st.toast("✅ Solicitudes programadas exitosamente")
            st.rerun()

def update_request_status(request_ids: list, request_status: str, admin_note: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        request = supabase.table("requests").update({
            "status": request_status,
            "admin_note": admin_note,
            "updated_at": now
        }).in_("id", request_ids).execute()
        st.toast("✅ Solicitud actualizada exitosamente")
        st.rerun()
        return request

    except Exception as e:
        st.error(f"Error updating request: {e.message}")

def select_request(request_id: int):
    try:
        request = supabase.table("requests").select(
            "username, status, request_category, measure_type, estimated_amount, details, admin_note"
        ).eq("id", request_id).execute()
        return request.data[0] if request.data else None
    except Exception as e:
        st.error(f"Error fetching request: {e.message}")
        return None

def list_all_requests(limit=200):
    try:
        requests = supabase.table("requests").select(
            "id, username, request_category, measure_type, estimated_amount, details, status, admin_note, created_at, updated_at"
        ).order("id", desc=True).limit(limit).execute()
        return requests.data
    except Exception as e:
        st.error(f"Error fetching requests: {e.message}")
        return []

def create_pickup(username: str, provider_name: str, pickup_date: str, admin_note: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        request = supabase.table("pickup").insert({
            "username": username,
            "provider_name": provider_name,
            "pickup_date": pickup_date,
            "admin_note": admin_note,
            "created_at": now,
            "updated_at": now
        }).execute()
        return request
    except Exception as e:
        st.error(f"Error creating pickup request: {e.message}")

def create_pickup_requests(request_ids: list, pickup_id: int):
    try:
        for request_id in request_ids:
            supabase.table("pickup_requests").insert({
                "request_id": request_id,
                "pickup_id": pickup_id
            }).execute()
    except Exception as e:
        st.error(f"Error creating pickup requests: {e.message}")

def display_schedule_pickup_table(pickup_data):
    try:
        if not pickup_data:
            st.info("📭 No hay recolecciones programadas aún. Programa una desde la pestaña de solicitudes pendientes.")
            return

        rows = pd.DataFrame(pickup_data)
        rows = rows[["id","pickup_status", "pickup_date", "provider_name", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows = rows[rows["pickup_status"] == "Programada"]
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False
        rows["request_ids"] = rows.index.map(lambda x: ", ".join(str(req["request_id"]) for req in select_pickup_requests(x)) if select_pickup_requests(x) else "N/A")

        if not rows.any().any():
            st.info("📭 No hay recolecciones programadas aún. Programa una desde la pestaña de solicitudes pendientes.")
            return

        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","pickup_status", "pickup_date", "provider_name", "created_at", "updated_at", "request_ids"], 
            column_config={
                "id": "ID",
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    pinned=True
                ),
                "pickup_date": "Fecha de recolección",
                "provider_name": "Proveedor asignado",
                "request_ids": st.column_config.ListColumn(
                    "IDs de solicitudes asociadas"
                ),
                "pickup_status": st.column_config.MultiselectColumn(
                    "Estado",
                    options=get_enum_values("status_type"),
                    color=["blue", "yellow", "red", "green"]
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
        cols = st.columns(2)
        if selected_count > 0:
            if cols[1].button("❌ Cancelar", width="stretch"):
                cancel_pickup_form(
                    pickup_ids=displayed_table[displayed_table["Seleccionar"]].index.tolist()
                )
        if selected_count > 0 and selected_count < 2:
            if cols[0].button("🔁 Editar", width="stretch"):
                update_pickup_form(
                    pickup_id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0]
                )


    except Exception as e:
            st.error("❌ Error al cargar las recolecciones programadas.")

def display_all_pickup_table(pickup_data):
    try:   
        rows = pd.DataFrame(pickup_data)
        rows = rows[["id","pickup_status", "pickup_date", "provider_name", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False
        rows["request_ids"] = rows.index.map(lambda x: ", ".join(str(req["request_id"]) for req in select_pickup_requests(x)) if select_pickup_requests(x) else "N/A")

        displayed_table = st.data_editor(
            rows,
            key="all_pickups_table",
            width="stretch",
            disabled=["id","pickup_status", "pickup_date", "provider_name", "created_at", "updated_at", "request_ids"], 
            column_config={
                "id": "ID",
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    pinned=True
                ),
                "pickup_date": "Fecha de recolección",
                "provider_name": "Proveedor asignado",
                "request_ids": st.column_config.ListColumn(
                    "IDs de solicitudes asociadas"
                ),
                "pickup_status": st.column_config.MultiselectColumn(
                    "Estado",
                    options=get_enum_values("status_type"),
                    color=["blue", "yellow", "red", "green"]
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

    except Exception as e:
            st.info("📭 No hay recolecciones disponibles aún. Programa una desde la pestaña de solicitudes pendientes.")

def list_all_pickups(limit=200):
    try:
        pickups = supabase.table("pickup").select("*").order("id", desc=True).limit(limit).execute()
        return pickups.data
    except Exception as e:
        st.error(f"Error fetching pickups: {e.message}")

def select_pickup_requests(pickup_id: int):
    try:
        pickup_requests = supabase.table("pickup_requests").select(
            "request_id"
        ).eq("pickup_id", pickup_id).execute()
        return pickup_requests.data if pickup_requests.data else None
    except Exception as e:
        st.error(f"Error fetching pickup requests: {e.message}")
        return []

def cancel_pickups(pickup_ids: list, admin_note: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        ### Update pickup status to "Cancelada"
        pickup = supabase.table("pickup").update({
            "pickup_status": "Cancelada",
            "admin_note": admin_note,
            "updated_at": now
        }).in_("id", pickup_ids).execute()

        ### Update associated requests status to "Pendiente"
        for pickup_id in pickup_ids:
            associated_requests = select_pickup_requests(pickup_id)
            if associated_requests:
                request_ids = [req["request_id"] for req in associated_requests]
                update_request_status(
                    request_ids=request_ids,
                    request_status="Pendiente",
                    admin_note=admin_note
                )
        
        st.toast("✅ Recolección cancelada exitosamente")
        return pickup

    except Exception as e:
        st.error(f"Error canceling pickup: {e.message}")
    st.rerun()    

@st.dialog("Cancelar recolección", width="small")
def cancel_pickup_form(pickup_ids: list):
    st.write("### Confirmar cancelación de recolección")
    st.markdown("¿Estás seguro de que deseas cancelar las recolecciones seleccionadas? Esta acción actualizará el estado de las solicitudes asociadas a :blue-badge[Pendiente].")
    admin_note = st.text_input("Nota del administrador (opcional)")
    cols = st.columns(2)
    if cols[1].button("❌ Cancelar recolección", width="stretch"):
        cancel_pickups(
            pickup_ids=pickup_ids,
            admin_note=admin_note
        )
        st.toast("✅ Recolección cancelada exitosamente")
        st.rerun()
    if cols[0].button("⬅️ Volver", width="stretch"):
        st.close_dialog()

@st.dialog("Editar recolección", width="medium")
def update_pickup_form(pickup_id: int):
    with st.form("update_pickup_form"):
        st.write(f"### Editar recolección ID: {pickup_id}")
        pickup_date = st.date_input("Fecha de recolección")
        provider_name = st.selectbox("Proveedor asignado", options=get_providers())
        admin_note = st.text_area("Nota del administrador (opcional)")
        submitted = st.form_submit_button("Actualizar recolección")
        if submitted:
            update_pickup(
                pickup_id=pickup_id,
                pickup_date=pickup_date.isoformat(),
                provider_name=provider_name,
                admin_note=admin_note
            )

def update_pickup(pickup_id: int, pickup_date: str, provider_name: str, admin_note: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        pickup = supabase.table("pickup").update({
            "pickup_date": pickup_date,
            "provider_name": provider_name,
            "admin_note": admin_note,
            "updated_at": now
        }).eq("id", pickup_id).execute()
        st.toast("✅ Recolección actualizada exitosamente")
        st.rerun()
        return pickup

    except Exception as e:
        st.error(f"Error updating pickup: {e.message}")

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')



### Main page code ###
if ss["authentication_status"]:

    ### Navigation template ###

    ### Formulario de solicitud de servicio ###
    mc.logout_and_home('./pages/residuos_peligrosos.py')

    with st.container(border=True, height="stretch", width="stretch", horizontal_alignment="center"):
        st.write("##### Gestión de solicitudes")
        tabs = st.tabs(["📄 Solicitudes pendientes", "📊 Todas las solicitudes"])
        with tabs[0]:
            display_pending_requests_table(list_all_requests())
        with tabs[1]:
            display_all_requests_table(list_all_requests())
        st.write("##### Gestión de recolecciones")
        tabs = st.tabs(["🗑️ Recolecciones programadas", "📊 Todas las recolecciones"])
        with tabs[0]:
            display_schedule_pickup_table(list_all_pickups())
        with tabs[1]:
            display_all_pickup_table(list_all_pickups())
else:
    st.switch_page("./pages/login_home.py")
