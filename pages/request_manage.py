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

        if rows.empty:
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
                    color=mc.elevencolors
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
        if rows.empty:
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
                    color=mc.elevencolors
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
        return sorted(result.data)
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
                        color=mc.elevencolors
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

        if rows.empty:
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
        cols = st.columns(3)
        if selected_count > 0:
            if cols[2].button("❌ Cancelar", width="stretch"):
                cancel_pickup_form(
                    pickup_ids=displayed_table[displayed_table["Seleccionar"]].index.tolist()
                )
        if selected_count > 0 and selected_count < 2:
            if cols[1].button("🔁 Editar", width="stretch"):
                update_pickup_form(
                    pickup_id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0]
                )
            if cols[0].button("✅ Completar", width="stretch"):
                complete_pickup_form(
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

def complete_pickup(pickup_id: int, cert_recoleccion_path: str, cert_transformacion_disposicion_path: str, otros_documentos_path: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        ### Update pickup status to "Completada"
        pickup = supabase.table("pickup").update({
            "pickup_status": "Completada",
            "updated_at": now,
            "cert_recoleccion_path": cert_recoleccion_path,
            "cert_transformacion_path": cert_transformacion_disposicion_path,
            "otros_documentos_path": otros_documentos_path
        }).eq("id", pickup_id).execute()

        ### Update associated requests status to "Completada"
        associated_requests = select_pickup_requests(pickup_id)
        if associated_requests:
            request_ids = [req["request_id"] for req in associated_requests]
            update_request_status(
                request_ids=request_ids,
                request_status="Completada"
            )
        
        st.toast("✅ Recolección completada exitosamente")
        return pickup

    except Exception as e:
        st.error(f"Error completing pickup: {e}")
    st.rerun()

@st.dialog("Completar recolección", width="medium")
def complete_pickup_form(pickup_id: int):
    st.write("### Residuos recolectados")
    displayed_table = display_real_ammount_table(
        request_ids=[req["request_id"] for req in select_pickup_requests(pickup_id)]
    )

    st.divider()

    st.write("### Adjuntar evidencia de recolección")
    cert_recoleccion_file = st.file_uploader("Sube el certificado de recolección (PDF)", type=["pdf"])
    cert_transformacion_disposicion_file = st.file_uploader("Sube el certificado de transformación o disposición final (PDF)", type=["pdf"])
    otros_documentos_files = st.file_uploader("Sube otros documentos relevantes (PDF)", type=["pdf"], accept_multiple_files=True)

    submitted = st.button("✅ Completar recolección")
    if submitted:
        missing = []
        if not cert_recoleccion_file:
            missing.append("Certificado de recolección")
        if not cert_transformacion_disposicion_file:
            missing.append("Certificado de transformación o disposición final")
        if missing:
            st.toast(f"Por favor, sube los siguientes documentos obligatorios: {', '.join(missing)}", icon="❌")
            return
        zero_values = displayed_table['real_ammount'] <= 0
        if zero_values.any():
            st.toast("Por favor, ingresa cantidades reales mayores a cero para todos los tipos de residuos recolectados.", icon="❌")
            return
        cert_recoleccion_path = mc.path_file(pickup_id, "certificado_recoleccion", cert_recoleccion_file)
        cert_transformacion_disposicion_path = mc.path_file(pickup_id, "certificado_transformacion_disposicion", cert_transformacion_disposicion_file)
        otros_documentos_paths = []
        if otros_documentos_files:
            otros_documentos_paths = mc.path_files_multiple(pickup_id, "otros_documentos", otros_documentos_files)
        otros_documentos_path = ", ".join(otros_documentos_paths) if otros_documentos_paths else None


        try:    
            mc.save_file(cert_recoleccion_file, cert_recoleccion_path)
            mc.save_file(cert_transformacion_disposicion_file, cert_transformacion_disposicion_path)
            if otros_documentos_files and otros_documentos_paths:
                for file_uploader, file_path in zip(otros_documentos_files, otros_documentos_paths):
                    mc.save_file(file_uploader, file_path)

            insert_residues_collected(
                displayed_table,
                pickup_id
            ) ### for some reason this function wont work if placed after the next function call

            complete_pickup(
                pickup_id=pickup_id,
                cert_recoleccion_path=cert_recoleccion_path,
                cert_transformacion_disposicion_path=cert_transformacion_disposicion_path,
                otros_documentos_path=otros_documentos_path
            )

            st.toast("✅ Recolección completada exitosamente")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.toast(f"❌ Error al completar la recolección: {e}")
            return

def display_real_ammount_table(request_ids: list):
    try:
        df = pd.DataFrame(list_all_requests())
        df = df[df["id"].isin(request_ids)]
        df = df.explode("request_category")[["request_category"]]
        df = df.drop_duplicates().reset_index(drop=True)
        df.sort_values(by="request_category", inplace=True)
        df["measure_type"] = df["request_category"].apply(lambda x: "m3" if x in ["Sólidos con aceite", "Aceites usados"] else "kg")
        df["real_ammount"] = 0
        df.set_index("request_category", inplace=True)
        real_ammount_table = st.data_editor(
            df,
            num_rows="dynamic",
            width="stretch",
            # hide_index=True,
            # disabled=["request_category"],
            column_config={
                "request_category": st.column_config.SelectboxColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_type"),
                    default="Aceites usados",
                    required=True
                ),
                "measure_type": st.column_config.SelectboxColumn(
                    "Tipo de unidad",
                    options=["kg", "m3"],
                    default="kg",
                    required=True
                ),
                "real_ammount": st.column_config.NumberColumn(
                    "Cantidad real recolectada",
                    min_value=0,
                    step=0.01,
                    default=0,
                    required=True
                )
            }
        )
        return real_ammount_table
    except Exception as e:
            st.write(f"No hay solicitudes pendientes disponibles")

def insert_residues_collected(df: pd.DataFrame, pickup_id: int):
    try:
        records = df.reset_index().to_dict('records')
        print(f'Step 1: Records to insert: {records}')
        for record in records:
            record['pickup_id'] = pickup_id
        print(f'Step 2: Records to insert with pickup_id: {records}')
        insert = supabase.table("residues_collected").insert(records).execute()
        print(f'Step 3: Insert result: {insert}')
        return insert
    except Exception as e:
        st.toast(f"Error inserting residues collected: {e}")


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
