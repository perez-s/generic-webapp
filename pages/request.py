### Minimal import for a Streamlit page ###
import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import modules.common as mc
import modules.auth as mauth

### Page specific imports ###
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import locale
import pandas as pd
from dateutil import parser

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

### Initialize Supabase client ###
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

### Functions for the page ###
@st.dialog("Editar solicitud", width="medium")
def update_request_form(id:int, request_category_default:list, measure_type_default: str, estimated_amount_default: float, details_default: str):
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
            options=get_enum_values("residue_category"),
            default=request_category_default
        )
        col1,col2 = st.columns(2)
        with col1:
            measure_type = st.selectbox("Tipo de unidades", options=get_enum_values("measure_unit"), index=get_enum_values("measure_unit").index(measure_type_default))
        with col2:
            estimated_amount = st.number_input("Cantidad estimada", min_value=0.1, step=0.1, value=float(estimated_amount_default))
        details = st.text_area("Comentarios", value=details_default)
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            request = update_request(id, request_category, measure_type, estimated_amount, details)
            mc.send_email(to_email=[ss["email"],mc.get_email().get('sostenibilidad')], operation='Update', supabase_return=request.data[0]),           
            st.toast("✅ Solicitud actualizada exitosamente")
            st.rerun()

def update_request(request_id: int, request_category:list, measure_type: str, estimated_amount: float,details: str):
    try:
        request = supabase.table("requests").update({
            "request_category": request_category,
            "measure_type": measure_type,
            "estimated_amount": estimated_amount,
            "details": details,
        }).eq("id", request_id).execute()
        return request

    except Exception as e:
        st.toast(f"❌ Error al actualizar la solicitud: {e}")

def select_request(request_id: int):
    try:
        request = supabase.table("requests").select(
            "request_category, measure_type, estimated_amount, details"
        ).eq("id", request_id).execute()
        return request.data[0] if request.data else None
    except Exception as e:
        st.toast(f"❌ Error al obtener la solicitud: {e}")
        return None

def cancel_request(ids: list):
    try:
        for request_id in ids:
            supabase.table("requests").update(
                {
                    "current_status": "Cancelada",
                 }
            ).eq("id", request_id).execute()
        return st.toast("✅ Solicitudes canceladas exitosamente")
    except Exception as e:
        return st.toast(f"❌ Error al cancelar solicitudes: {e}")

def create_request_button():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Crear nueva solicitud", width="stretch"):
            create_request_form() 

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return sorted(result.data)
    except Exception as e:
        print(f"Error fetching enum values: {e}")

def create_request(userid: int, request_category:list, measure_type: str, estimated_amount: float,details: str):
    try:
        request = supabase.table("requests").insert({
            "userid": userid,
            "request_category": request_category,
            "measure_type": measure_type,
            "estimated_amount": estimated_amount,
            "details": details,
            "current_status": "Pendiente",
        }).execute()
        mc.send_email(to_email=[ss["email"],mc.get_email().get('sostenibilidad')], operation='Creation', supabase_return=request.data[0])
        st.toast("✅ Solicitud creada exitosamente")
        st.rerun()
        return request
    except Exception as e:
        st.toast(f"❌ Error al crear la solicitud: {e}")

def list_all_requests(limit=200):
    try:
        requests = supabase.table("requests").select(
            "id, users(*), request_category, measure_type, estimated_amount, details, current_status, admin_note, created_at, updated_at"
        ).order("id", desc=True).limit(limit).execute()
        return requests.data
    except Exception as e:
        st.toast(f"❌ Error al obtener las solicitudes: {e}") 

@st.dialog("Crear solicitud", width="medium")
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
            options=get_enum_values("residue_category")
            ,
        )
        col1,col2 = st.columns(2)
        with col1:
            measure_type = st.selectbox("Tipo de unidades", options=get_enum_values("measure_unit"), index=get_enum_values("measure_unit").index("kg"))
        with col2:
            estimated_amount = st.number_input("Cantidad estimada", min_value=0.1, step=0.1)
        details = st.text_area("Comentarios")
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            if mc.validate_residue_types(request_category) == False:
                return
            userid = mauth.get_user_id(ss["username"])
            try:        
                create_request(userid, request_category, measure_type, estimated_amount, details)
            except Exception as e:
                st.toast(f"❌ Error al crear la solicitud: {e}")

def display_pending_requests_table(requests_data, userid):
    try:
        with st.container(border=True, width="stretch"):
            rows = pd.DataFrame(requests_data)
            rows = rows[["id","users","current_status","request_category","measure_type","estimated_amount","created_at","updated_at"]]
            rows["userid"] = rows["users"].apply(lambda x: x["id"] if isinstance(x, dict) else x)
            rows["username"] = rows["users"].apply(lambda x: x["username"] if isinstance(x, dict) else x)
            rows = rows[(rows["current_status"] == "Pendiente") & (rows["userid"] == userid)]
            rows = rows[["id","created_at","updated_at","username","current_status","request_category","measure_type","estimated_amount"]]
            if rows.empty:
                st.info(f"📭 No hay solicitudes pendientes disponibles")
                return
            rows["created_at"] = rows["created_at"].apply(lambda x: parser.parse(x)).dt.tz_convert('America/Bogota')
            rows["updated_at"] = rows["updated_at"].apply(lambda x: parser.parse(x)).dt.tz_convert('America/Bogota')   
            # rows.set_index("id", inplace=True)
    
            rows["Seleccionar"] = False

            top_menu_container = st.container()
            pagination = st.container()

            bottom_menu = st.columns((4, 1, 1))
            with bottom_menu[2]:
                batch_size = st.selectbox("Registros", options=[10, 25, 50, 100])
            with bottom_menu[1]:
                total_pages = (
                    int(len(rows) / batch_size) if int(len(rows) / batch_size) > 0 else 1
                )
                if ( batch_size * total_pages ) < len(rows):
                    total_pages += 1
                page_numbers = list(range(1, total_pages + 1))
                current_page = st.selectbox(
                    'Página', options=page_numbers, index=0, key="page_selector"
                )
            with bottom_menu[0]:
                st.markdown(f"Página **{current_page}** de **{total_pages}** ")
            
            top_menu = top_menu_container.columns(6)
            with top_menu[5]:
                label_map = {
                    "id": "ID",
                    "username": "Usuario",
                    "current_status": "Estado",
                    "request_category": "Categorías de residuos",
                    "measure_type": "Tipo de unidad",
                    "estimated_amount": "Cantidad estimada",
                    "created_at": "Fecha de creación",
                    "updated_at": "Última modificación",
                }
                available_cols = [k for k in label_map.keys() if k in rows.columns]
                sort_field = st.selectbox(
                    "Ordenar por",
                    options=available_cols,
                    index=available_cols.index("created_at"),
                    format_func=lambda x: label_map.get(x, x)
                )
            with top_menu[4]:
                sort_direction = st.radio(
                    "Dirección", options=["⬆️", "⬇️"], horizontal=True
                )
            rows = rows.sort_values(
                by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
            )

            rows = mc.split_frame(rows, batch_size)
            
            displayed_table = pagination.data_editor(
                data=rows[current_page - 1],
                width="stretch",
                disabled=["id", "username","current_status", "request_category", "measure_type", "estimated_amount", "created_at", "updated_at"], 
                hide_index=True,
                column_config={
                    "id": "ID",
                    "Seleccionar": st.column_config.CheckboxColumn(
                        "Seleccionar",
                        pinned=True
                    ),
                    "username": "Usuario",
                    "current_status": "Estado",
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
                    "created_at": st.column_config.DatetimeColumn(
                        "Fecha de creación",
                        format="YYYY/MM/DD HH:mm"
                    ),  
                    "updated_at": st.column_config.DatetimeColumn(
                        "Última modificación",
                        format="YYYY/MM/DD HH:mm"
                    )
                }
            )
            
            selected_count = displayed_table.Seleccionar.sum()

            col1, col2 = st.columns(2)
            if selected_count > 0 and selected_count < 2:
                with col1:    
                    if st.button("🔁 Editar solicitud", width="stretch"):
                        default_options = select_request(displayed_table[displayed_table["Seleccionar"]]["id"].tolist()[0])
                        update_request_form(
                            id=displayed_table[displayed_table["Seleccionar"]]["id"],
                            request_category_default=default_options["request_category"],
                            measure_type_default=default_options["measure_type"],
                            estimated_amount_default=default_options["estimated_amount"],
                            details_default=default_options["details"]
                        )
            if selected_count > 0 or selected_count >= 2:
                with col2:
                    if st.button("❌ Cancelar solicitudes", width="stretch"):
                        confirm_delete_dialog(displayed_table[displayed_table["Seleccionar"]]["id"].tolist())
           
    except Exception as e:
        st.info(f"Error al mostrar las solicitudes {e}")

def display_all_requests_table(requests_data, userid):
    try:
        rows = pd.DataFrame(requests_data)
        rows = rows[["id","users","current_status","request_category","measure_type","estimated_amount","created_at","updated_at", "admin_note"]]
        rows["userid"] = rows["users"].apply(lambda x: x["id"] if isinstance(x, dict) else x)
        rows["username"] = rows["users"].apply(lambda x: x["username"] if isinstance(x, dict) else x)
        rows = rows[(rows["userid"] == userid)]
        rows = rows[["id","username","created_at","updated_at","current_status","request_category","measure_type","estimated_amount", "admin_note"]]
        rows["created_at"] = rows["created_at"].apply(lambda x: parser.parse(x)).dt.tz_convert('America/Bogota')
        rows["updated_at"] = rows["updated_at"].apply(lambda x: parser.parse(x)).dt.tz_convert('America/Bogota')
        if rows.empty:
            st.info(f"📭 No hay solicitudes pendientes disponibles")
            return
        rows.set_index("id", inplace=True)

        top_menu_container = st.container()
        pagination = st.container()

        bottom_menu = st.columns((4, 1, 1))
        with bottom_menu[2]:
            batch_size = st.selectbox("Registros", options=[10, 25, 50, 100], key="all_requests_batch_size")
        with bottom_menu[1]:
            total_pages = (
                int(len(rows) / batch_size) if int(len(rows) / batch_size) > 0 else 1
            )
            if ( batch_size * total_pages ) < len(rows):
                total_pages += 1
            page_numbers = list(range(1, total_pages + 1))
            current_page = st.selectbox(
                'Página', options=page_numbers, index=0, key="all_requests_page_selector"
            )
        with bottom_menu[0]:
            st.markdown(f"Página **{current_page}** de **{total_pages}** ")
        
        top_menu = top_menu_container.columns(6)
        with top_menu[5]:
            label_map = {
                "id": "ID",
                "Seleccionar": "Seleccionar",
                "username": "Usuario",
                "current_status": "Estado",
                "request_category": "Categorías de residuos",
                "measure_type": "Tipo de unidad",
                "estimated_amount": "Cantidad estimada",
                "created_at": "Fecha de creación",
                "updated_at": "Última modificación",
            }
            available_cols = [k for k in label_map.keys() if k in rows.columns]
            sort_field = st.selectbox(
                "Ordenar por",
                options=available_cols,
                index=available_cols.index("created_at"),
                format_func=lambda x: label_map.get(x, x),
                key="all_requests_sort_field"
            )
        with top_menu[4]:
            sort_direction = st.radio(
                "Dirección", options=["⬆️", "⬇️"], horizontal=True, key="all_requests_sort_direction"
            )
        rows = rows.sort_values(
            by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
        )

        rows = mc.split_frame(rows, batch_size)

        pagination.dataframe(
            rows[current_page - 1],
            width="stretch",
            hide_index=True,
            column_config={
                "id": "ID",
                "username": "Usuario",
                "current_status": "Estado",
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
                "created_at": st.column_config.DatetimeColumn(
                    "Fecha de creación",
                    format="YYYY/MM/DD HH:mm"
                    ),
                "updated_at": st.column_config.DatetimeColumn(
                    "Última modificación",
                    format="YYYY/MM/DD HH:mm"
                    ),
                "admin_note": "Nota del administrador"
            }
        )
    except Exception as e:
        st.info(f"Error al mostrar las solicitudes {e}")

@st.dialog("⚠️ Confirmar eliminación")
def confirm_delete_dialog(request_ids: list):
    """Confirmation dialog for deleting requests."""
    st.warning(f"¿Estás seguro de que deseas cancelar {len(request_ids)} solicitud(es)?")
    st.markdown("Esta acción cancelará:")
    st.markdown("- La solicitud ya no estará activa.")
    st.error("⚠️ Esta acción no se puede deshacer.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancelar", width="stretch", type="secondary"):
            st.rerun()
    with col2:
        if st.button("✅ Confirmar", width="stretch", type="primary"):
            if cancel_request(request_ids):
                time.sleep(1)
                st.rerun()

### Page layout and logic ###
if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:

    userid = mauth.get_user_id(ss["username"])

    ### Navigation template ###

    ### Formulario de solicitud de servicio ###
    mc.logout_and_home('./pages/residuos_peligrosos.py')

    st.markdown("### 📋 Solicitud de servicio")

    create_request_button()

    st.divider()
    all_requests = list_all_requests()
    tab1, tab2 = st.tabs(["📄 Solicitudes pendientes", "📊 Todas las solicitudes"])
    with tab1:
        display_pending_requests_table(all_requests, userid)
    with tab2:
        display_all_requests_table(all_requests, userid)

else:
    st.switch_page("./pages/login_home.py")
