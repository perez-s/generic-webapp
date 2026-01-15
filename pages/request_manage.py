import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import modules.common as mc
import modules.auth as mauth
import modules.queries as mq

### Page specific imports ###
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import locale
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Cargar variables de entorno y configurar Supabase
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_pickup_date_by_request_id(pickup_id: int):
    try:
        # Join pickup_requests with pickup table
        result = supabase.table("pickup").select(
            "id, pickup_date, admin_note, pickup_requests(request_id)"
        ).eq("id", pickup_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching pickup date: {e}")
        return None

def translate_categories(categories: list):
    translation_pairs = [
        ("Aceites usados", "Y9-Aceite usado"),
        ("Aerosoles", "Y12-Aerosoles"),
        ("Baterías", "Y31-Baterías plomo ácido"),
        ("Baterías de ion litio", "Z-Baterías de ion litio"),
        ("Biosanitarios", "Y1-Biosanitarios"),
        ("Luminarias", "Y29-Bombillos, tubos y lámparas"),
        ("Pilas", "Y23-Pilas y baterías"),
        ("Pinturas", "Y12-Pinturas"),
        ("RAEE", "A1180-Aparatos eléctricos y electrónicos"),
        ("Sólidos con aceite", "Y9-Sólidos contaminados con aceite"),
        ("Tóneres", "Y12-Tóneres"),
        ("Otros peligrosos", "Z-Otros peligrosos"),
    ]
    translation_map = {}
    for word, translation in translation_pairs:
        translation_map[word] = translation
        translation_map[translation] = word
    return [translation_map[category] if category in translation_map else category for category in categories]

def get_providers():
    try:
        providers = supabase.table("providers").select("provider_name").eq("provider_is_active", True).execute()
        return [provider['provider_name'] for provider in providers.data]
    except Exception as e:
        st.error(f"Error fetching providers: {e}")
        return []

def display_pending_requests_table(requests_data):
    try:
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","users","current_status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]
        rows["userid"] = rows["users"].apply(lambda x: x["id"] if isinstance(x, dict) else x)
        rows["username"] = rows["users"].apply(lambda x: x["username"] if isinstance(x, dict) else x)
        rows = rows[["id","username","current_status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]       
        rows = rows[rows["current_status"] == "Pendiente"]
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
            disabled=["id","username","current_status", "request_category", "measure_type", "estimated_amount", "created_at", "updated_at"], 
            column_config={
                "id": "ID",
                "username": "Usuario",
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    pinned=True
                ),
                "request_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_category"),
                    color=mc.elevencolors
                ),
                "measure_type": "Tipo de unidad",
                "estimated_amount": "Cantidad estimada",
                "current_status": st.column_config.MultiselectColumn(
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
        selected_rows = displayed_table[displayed_table["Seleccionar"]]
        selected_count = len(selected_rows)
        if selected_count > 0:
            if st.button("🗓️ Agendar solicitud", width="stretch"):
                schedule_request_form(
                    ids=selected_rows.index.tolist(),
                    all_requests=requests_data
                )
    except Exception as e:
            st.write(f'Error loading pending requests: {e}') 

def display_all_requests_table(requests_data):
    try:   
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","users","current_status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]
        rows["userid"] = rows["users"].apply(lambda x: x["id"] if isinstance(x, dict) else x)
        rows["username"] = rows["users"].apply(lambda x: x["username"] if isinstance(x, dict) else x)
        rows = rows[["id","username","current_status", "request_category","measure_type","estimated_amount", "created_at", "updated_at"]]       
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)
        if rows.empty:
            st.info("📭 No hay solicitudes disponibles aun.")
            return

        displayed_table = st.dataframe(
            rows,
            width="stretch",
            column_config={
                "id": "ID",
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    pinned=True
                ),
                "request_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_category"),
                    color=mc.elevencolors
                ),
                "measure_type": "Tipo de unidad",
                "estimated_amount": "Cantidad estimada",
                "current_status": st.column_config.MultiselectColumn(
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
            st.info(f"📭 No hay solicitudes pendientes disponibles") 

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return sorted(result.data)
    except Exception as e:
        print(f"Error fetching enum values: {e}")

@st.dialog("Programar solicitudes", width="large")
def schedule_request_form(ids: list, all_requests):
    providers = get_providers()
    request_usernames = list(set([select_request_email(rid) for rid in ids]))
    emails = []
    for username in request_usernames:
        email = mc.get_email().get(username)
        emails.append(email)

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
            df = pd.DataFrame(all_requests)
            df["username"] = df["users"].apply(lambda x: x["username"] if isinstance(x, dict) else x)
            df = df[df["id"].isin(ids)]
            df.set_index("id", inplace=True)
            st.dataframe(
                df[["username","request_category", "measure_type", "estimated_amount"]],
                width="stretch",
                column_config={
                    "username": "Usuario",
                    "request_category": st.column_config.MultiselectColumn(
                        "Categorías de residuos",
                        options=get_enum_values("residue_category"),
                        color=mc.elevencolors
                    ),
                    "measure_type": "Unidades",
                    "estimated_amount": "Cantidad estimada"
                }
                )


        if submitted:
            if admin_note == "":
                admin_note = None
            with st.spinner("⏳ Programando solicitudes..."):
                pickup = create_pickup(
                    userid=userid,
                    providerid=mauth.get_provider_id(provider_name),
                    pickup_date=pickup_date.isoformat(),
                    admin_note=admin_note
                )
                pickup_requests = create_pickup_requests(
                    request_ids=ids,
                    pickup_id=pickup.data[0]["id"]
                )
                request = update_request_status(
                    request_ids=ids,
                    request_status="Programada",
                    admin_note=admin_note
                )
                mc.send_email(supabase_return=get_pickup_date_by_request_id(pickup.data[0]["id"]), to_email=[mc.get_email().get('sostenibilidad')] + emails, operation='Schedule')
            st.toast("✅ Solicitudes programadas exitosamente")
            st.rerun()

def update_request_status(request_ids: list, request_status: str, admin_note: str = None):
    try:
        request = supabase.table("requests").update({
            "current_status": request_status,
            "admin_note": admin_note,
        }).in_("id", request_ids).execute()
        return request

    except Exception as e:
        st.error(f"Error updating request: {e}")

def select_request_email(request_id: int):
    try:
        request = supabase.table("requests").select(
            "users(username)"
        ).eq("id", request_id).execute()
        return request.data[0]["users"]["username"] if request.data else None
    except Exception as e:
        st.error(f"Error fetching request: {e}")
        return None

def list_all_requests(limit=200):
    try:
        requests = supabase.table("requests").select(
            "id, users(*), request_category, measure_type, estimated_amount, details, current_status, admin_note, created_at, updated_at"
        ).order("id", desc=True).limit(limit).execute()
        return requests.data
    except Exception as e:
        st.error(f"Error fetching requests: {e}")
        return []

def create_pickup(userid: str, providerid: str, pickup_date: str, admin_note: str = None):
    try:
        request = supabase.table("pickup").insert({
            "userid": userid,
            "providerid": providerid,
            "pickup_date": pickup_date,
            "admin_note": admin_note,
        }).execute()
        return request
    except Exception as e:
        st.error(f"Error creating pickup request: {e}")

def create_pickup_requests(request_ids: list, pickup_id: int):
    try:
        for request_id in request_ids:
            supabase.table("pickup_requests").insert({
                "request_id": request_id,
                "pickup_id": pickup_id
            }).execute()
    except Exception as e:
        st.error(f"Error creating pickup requests: {e}")

def display_schedule_pickup_table(pickup_data):
    try:
        if not pickup_data:
            st.info("📭 No hay recolecciones programadas aún. Programa una desde la pestaña de solicitudes pendientes.")
            return
        rows = pd.DataFrame(pickup_data)
        rows = rows[["id","providers","pickup_status", "pickup_date", "created_at", "updated_at"]]
        rows["provider_name"] = rows["providers"].apply(lambda x: x["provider_name"] if isinstance(x, dict) else x)
        rows = rows[["id","provider_name","pickup_status", "pickup_date", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows = rows[rows["pickup_status"] == "Programada"]
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False

        # Fetch all pickup requests for the displayed pickups in a single query
        pickup_ids = rows.index.tolist()
        pickup_requests_by_pickup_id = {}
        if pickup_ids:
            response = supabase.table("pickup_requests").select("pickup_id, request_id").in_("pickup_id", pickup_ids).execute()
            data = getattr(response, "data", None) or response.get("data", [])
            for record in data:
                pickup_id = record.get("pickup_id")
                request_id = record.get("request_id")
                if pickup_id is not None and request_id is not None:
                    pickup_requests_by_pickup_id.setdefault(pickup_id, []).append(request_id)

        rows["request_ids"] = rows.index.map(
            lambda x: ", ".join(str(req_id) for req_id in pickup_requests_by_pickup_id.get(x, [])) or "N/A"
        )
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
        rows = rows[["id", "providers", "pickup_status", "pickup_date", "created_at", "updated_at"]]
        rows["provider_name"] = rows["providers"].apply(lambda x: x["provider_name"] if isinstance(x, dict) else x)
        rows = rows[["id","provider_name","pickup_status", "pickup_date", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False
        pickup_ids = rows.index.tolist()
        pickup_requests_by_pickup_id = {}
        if pickup_ids:
            response = supabase.table("pickup_requests").select("pickup_id, request_id").in_("pickup_id", pickup_ids).execute()
            data = getattr(response, "data", None) or response.get("data", [])
            for record in data:
                pickup_id = record.get("pickup_id")
                request_id = record.get("request_id")
                if pickup_id is not None and request_id is not None:
                    pickup_requests_by_pickup_id.setdefault(pickup_id, []).append(request_id)

        rows["request_ids"] = rows.index.map(
            lambda x: ", ".join(str(req_id) for req_id in pickup_requests_by_pickup_id.get(x, [])) or "N/A"
        )


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

        selected_count = displayed_table.Seleccionar.sum()
        cols = st.columns(3)
        if selected_count > 0 and selected_count < 2:
            if cols[1].button("👁️ Consultar", width="stretch"):
                pickup_detail_view(
                    pickup_id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0]
                )       

    except Exception as e:
            st.info("📭 No hay recolecciones disponibles aún. Programa una desde la pestaña de solicitudes pendientes.")

def list_all_pickups(limit=200):
    try:
        pickups = supabase.table("pickup").select("*", "providers(*)").order("id", desc=True).limit(limit).execute()
        return pickups.data
    except Exception as e:
        st.error(f"Error fetching pickups: {e}")

def select_pickup_requests(pickup_id: int):
    try:
        pickup_requests = supabase.table("pickup_requests").select(
            "request_id"
        ).eq("pickup_id", pickup_id).execute()
        return pickup_requests.data if pickup_requests.data else None
    except Exception as e:
        st.error(f"Error fetching pickup requests: {e}")
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
        st.error(f"Error canceling pickup: {e}")
    st.rerun()    

@st.dialog("Cancelar recolección", width="small")
def cancel_pickup_form(pickup_ids: list):
    st.write("### Confirmar cancelación de recolección")
    st.markdown("¿Estás seguro de que deseas cancelar las recolecciones seleccionadas? Esta acción actualizará el estado de las solicitudes asociadas a :blue-badge[Pendiente].")
    admin_note = st.text_input("Nota del administrador (opcional)")
    cols = st.columns(2)
    if cols[1].button("❌ Cancelar recolección", width="stretch"):
        pickup = cancel_pickups(
            pickup_ids=pickup_ids,
            admin_note=admin_note
        )
        for pid in pickup_ids:
            data = get_pickup_date_by_request_id(pid)
            request_ids = [request['request_id'] for request in data['pickup_requests']]
            request_usernames = list(set([select_request_email(rid) for rid in request_ids]))
            emails = []
            for username in request_usernames:
                email = mc.get_email().get(username)
                emails.append(email)

            mc.send_email(to_email=[mc.get_email().get('sostenibilidad')] + emails, operation='Cancelled', supabase_return=data)
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
            pickup = update_pickup(
                pickup_id=pickup_id,
                pickup_date=pickup_date.isoformat(),
                provider_name=provider_name,
                admin_note=admin_note
            )
            st.toast("✅ Recolección actualizada exitosamente")
            st.rerun()

def update_pickup(pickup_id: int, pickup_date: str, provider_name: str, admin_note: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        pickup = supabase.table("pickup").update({
            "pickup_date": pickup_date,
            "provider_name": provider_name,
            "admin_note": admin_note,
            "updated_at": now
        }).eq("id", pickup_id).execute()
        return pickup

    except Exception as e:
        st.error(f"Error updating pickup: {e}")

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
    displayed_table = display_ask_real_ammount_table()

    st.divider()

    st.write("### Adjuntar evidencia de recolección")
    cert_recoleccion_file = st.file_uploader("Sube el certificado de recolección (PDF)", type=["pdf"])
    cert_transformacion_disposicion_files = st.file_uploader("Sube el certificado de transformación o disposición final (PDF)", type=["pdf"], accept_multiple_files=True)
    otros_documentos_files = st.file_uploader("Sube otros documentos relevantes (PDF)", type=["pdf"], accept_multiple_files=True)

    submitted = st.button("✅ Completar recolección")
    if submitted:
        missing = []
        if not cert_recoleccion_file:
            missing.append("Certificado de recolección")
        if not cert_transformacion_disposicion_files:
            missing.append("Certificado de transformación o disposición final")
        if missing:
            st.toast(f"Por favor, sube los siguientes documentos obligatorios: {', '.join(missing)}", icon="❌")
            return
        zero_values = displayed_table['real_ammount'] <= 0
        if zero_values.any():
            st.toast("Por favor, ingresa cantidades reales mayores a cero para todos los tipos de residuos recolectados.", icon="❌")
            return
        
        cert_recoleccion_path = mc.path_file(pickup_id, "certificado_recoleccion", cert_recoleccion_file)
        
        cert_transformacion_disposicion_paths = []
        if cert_transformacion_disposicion_files:
            cert_transformacion_disposicion_paths = mc.path_files_multiple(pickup_id, "certificado_transformacion_disposicion", cert_transformacion_disposicion_files)
        cert_transformacion_disposicion_path = ", ".join(cert_transformacion_disposicion_paths) if cert_transformacion_disposicion_paths else None        

        otros_documentos_paths = []
        if otros_documentos_files:
            otros_documentos_paths = mc.path_files_multiple(pickup_id, "otros_documentos", otros_documentos_files)
        otros_documentos_path = ", ".join(otros_documentos_paths) if otros_documentos_paths else None


        try:    
            mc.save_file(cert_recoleccion_file, cert_recoleccion_path)
            if cert_transformacion_disposicion_files and cert_transformacion_disposicion_paths:
                for file_uploader, file_path in zip(cert_transformacion_disposicion_files, cert_transformacion_disposicion_paths):
                    mc.save_file(file_uploader, file_path)
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

def display_ask_real_ammount_table():
    try:
        df = pd.DataFrame(columns=['residue_category', 'measure_type', 'real_ammount'])
        df.set_index("residue_category", inplace=True)
        real_ammount_table = st.data_editor(
            df,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "residue_category": st.column_config.SelectboxColumn(
                    "Categorías de residuos",
                    options=mq.get_residuo_corriente_names(),
                    default=translate_categories(["Aceites usados"])[0],
                    required=True
                ),
                "measure_type": st.column_config.SelectboxColumn(
                    "Tipo de unidad",
                    options=get_enum_values("measure_unit"),
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
        
        # Calculate total in kg
        if not real_ammount_table.empty:
            conversion_factors = {
                'kg': 1,
                'g': 0.001,
                't': 1000,
                'ton': 1000,
                'mg': 0.000001,
                'l': 1
            }
            
            total_kg = 0
            for idx, row in real_ammount_table.iterrows():
                measure = row['measure_type']
                amount = row['real_ammount']
                factor = conversion_factors.get(measure, 1)
                total_kg += amount * factor
            
            st.metric("Total", f"{total_kg:.2f} kg")
        
        return real_ammount_table
    except Exception as e:
            st.exception(e)

def insert_residues_collected(df: pd.DataFrame, pickup_id: int):
    try:
        df = df.reset_index()[["residue_category", "measure_type", "real_ammount"]]
        df.set_index("residue_category", inplace=True)
        records = df.reset_index().to_dict('records')
        for record in records:
            record['pickup_id'] = pickup_id
        insert = supabase.table("residues_collected").insert(records).execute()
        return insert
    except Exception as e:
        st.exception(e)

@st.dialog("📋 Detalle de la recolección", width="large")
def pickup_detail_view(pickup_id: int):
    """Display detailed view of a pickup with all information and downloadable files."""
    try:
        pickup = select_pickup(pickup_id)
        if not pickup:
            st.error("No se pudo cargar la información de la recolección.")
            return
        
        st.write("### Materiales recolectados")
        
        display_real_ammount_table(pickup_id)
        
        st.divider()
        st.write("### Documentos de soporte de la recolección")

        st.markdown("**Certificado de recolección**")
        certificado_recoleccion_path = pickup.get('cert_recoleccion_path', '')
        if certificado_recoleccion_path and os.path.exists(certificado_recoleccion_path):
            with st.expander("📄 Ver Certificado de recolección"):
                try:
                    with open(certificado_recoleccion_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                        st.pdf(pdf_data, key="view_certificado_recoleccion_pdf")
                except Exception as e:
                    st.error(f"Error cargando PDF: {e}")
                    st.markdown("**Certificado de recolección**")
        
        st.markdown("**Certificados de transformación**")
        with st.expander("📄 Ver certificados de transformación", expanded=False):
            otros_documentos_path = pickup.get('cert_transformacion_path', '')
            if otros_documentos_path:
                otros_documentos_list = [p.strip() for p in otros_documentos_path.split(",") if p.strip()]
                if otros_documentos_list:
                    has_files = False
                    for idx, doc_path in enumerate(otros_documentos_list):
                        if os.path.exists(doc_path):
                            has_files = True
                            with st.expander(f"📄 Ver Documento {idx+1}"):
                                try:
                                    with open(doc_path, "rb") as pdf_file:
                                        pdf_data = pdf_file.read()
                                        st.pdf(pdf_data, key=f"view_certificado_transformacion_pdf_{idx}")
                                except Exception as e:
                                    st.error(f"Error cargando PDF: {e}")
                    if not has_files:
                        st.caption("No hay archivos disponibles")
                else:
                    st.caption("No hay archivos disponibles")
            else:
                st.caption("No hay archivos disponibles")

        st.markdown("**Otros documentos relevantes**")
        with st.expander("📄 Otros documentos relevantes", expanded=False):
            otros_documentos_path = pickup.get('otros_documentos_path', '')
            if otros_documentos_path:
                otros_documentos_list = [p.strip() for p in otros_documentos_path.split(",") if p.strip()]
                if otros_documentos_list:
                    has_files = False
                    for idx, doc_path in enumerate(otros_documentos_list):
                        if os.path.exists(doc_path):
                            has_files = True
                            with st.expander(f"📄 Ver Documento {idx+1}"):
                                try:
                                    with open(doc_path, "rb") as pdf_file:
                                        pdf_data = pdf_file.read()
                                        st.pdf(pdf_data, key=f"view_documento_pdf_{idx}")
                                except Exception as e:
                                    st.error(f"Error cargando PDF: {e}")
                    if not has_files:
                        st.caption("No hay archivos disponibles")
                else:
                    st.caption("No hay archivos disponibles")
            else:
                st.caption("No hay archivos disponibles")

    except Exception as e:
        st.error(f"Error cargando detalles de la recolección: {e}")

def select_pickup(pickup_id: int):
    try:
        request = supabase.table("pickup").select(
            "*"
        ).eq("id", pickup_id).execute()
        return request.data[0] if request.data else None
    except Exception as e:
        st.error(f"Error fetching pickup: {e}")
        return None

def display_real_ammount_table(pickup_id: int):
    try:
        residues = supabase.table("residues_collected").select(
            "residue_category, measure_type, real_ammount"
        ).eq("pickup_id", pickup_id).execute()
        rows = pd.DataFrame(residues.data)
        if rows.empty:
            st.info("📭 No hay materiales recolectados registrados para esta recolección.")
            return

        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["request_category", "measure_type", "real_ammount"],
            hide_index=True, 
            column_config={
                "request_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_category"),
                    color=mc.elevencolors
                ),
                "measure_type": "Tipo de unidad",
                "real_ammount": "Cantidad recolectada"
            }
        )
        
        # Calculate total in kg
        if not displayed_table.empty:
            conversion_factors = {
                'kg': 1,
                'g': 0.001,
                't': 1000,
                'ton': 1000,
                'mg': 0.000001,
                'l': 1
            }
            
            total_kg = 0
            for idx, row in displayed_table.iterrows():
                measure = row['measure_type']
                amount = row['real_ammount']
                factor = conversion_factors.get(measure, 1)
                total_kg += amount * factor
            
            st.metric("Total", f"{total_kg:.2f} kg")
    except Exception as e:
            st.write(f"No hay materiales recolectados disponibles [{e}]")

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:
    userid = mauth.get_user_id(ss["username"])


    ### Navigation template ###

    ### Formulario de solicitud de servicio ###
    mc.logout_and_home('./pages/residuos_peligrosos.py')

    with st.container(border=True, height="stretch", width="stretch", horizontal_alignment="center"):
        st.write("##### Gestión de solicitudes")
        tabs0 = st.tabs(['Solicitudes', 'Recolecciones'])
        with tabs0[0]:
            # Fetch all requests once and reuse across tabs to avoid redundant queries
            all_requests = list_all_requests()
            tabs = st.tabs(["📄 Solicitudes pendientes", "📊 Todas las solicitudes"])
            with tabs[0]:
                display_pending_requests_table(all_requests)
            with tabs[1]:
                display_all_requests_table(all_requests)
        with tabs0[1]:
            all_pickups = list_all_pickups()
            tabs = st.tabs(["🗑️ Recolecciones programadas", "📊 Todas las recolecciones"])
            with tabs[0]:
                display_schedule_pickup_table(all_pickups)
            with tabs[1]:
                display_all_pickup_table(all_pickups)
else:
    st.switch_page("./pages/login_home.py")
