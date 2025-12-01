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
def delete_provider(provider_ids: list):
    """Delete one or more providers by their IDs and remove their files."""
    try:
        deleted_files = 0
        for provider_id in provider_ids:
            # Fetch file paths to delete files from disk
            provider = supabase.table("providers").select(
                "lic_amb_path, rut_path, ccio_path, other_docs_path"
            ).eq("id", provider_id).execute()
            
            if provider.data:
                file_paths = [
                    provider.data[0].get("lic_amb_path"),
                    provider.data[0].get("rut_path"),
                    provider.data[0].get("ccio_path"),
                    provider.data[0].get("other_docs_path")
                ]
                
                # Remove files from disk if they exist
                for file_path in file_paths:
                    if file_path and file_path.strip() and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            deleted_files += 1
                        except Exception as file_err:
                            print(f"Warning: Could not delete file {file_path}: {file_err}")
            
            # Delete provider from database
            supabase.table("providers").delete().eq("id", provider_id).execute()
        
        st.toast(f"✅ {len(provider_ids)} proveedor(es) y {deleted_files} archivo(s) eliminados exitosamente")
        return True
    
    except Exception as e:
        st.error(f"Error eliminando proveedor(es): {e}")
        return False

@st.dialog("⚠️ Confirmar eliminación")
def confirm_delete_dialog(provider_ids: list):
    """Confirmation dialog for deleting providers."""
    st.warning(f"¿Estás seguro de que deseas eliminar {len(provider_ids)} proveedor(es)?")
    st.markdown("Esta acción eliminará:")
    st.markdown("- Los registros de la base de datos")
    st.markdown("- Todos los archivos asociados (licencias, RUT, cámara de comercio, etc.)")
    st.error("⚠️ Esta acción no se puede deshacer.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancelar", width="stretch", type="secondary"):
            st.rerun()
    with col2:
        if st.button("🗑️ Eliminar", width="stretch", type="primary"):
            if delete_provider(provider_ids):
                time.sleep(1)
                st.rerun()

def update_provider(
        provider_id: int,
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
        other_docs_path: str,
        updated_at: str
    ):
    try:
        request = supabase.table("providers").update({
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
            "updated_at": updated_at
        }).eq("id", provider_id).execute()
        st.toast("✅ Proveedor actualizado exitosamente")
        st.rerun()
        return request

    except Exception as e:
        st.error(f"Error actualizando proveedor: {e}")

@st.dialog("Actualizar proveedor", width="large")
def update_provider_form(id: int,provider_name_default: str, provider_nit_default: int, provider_email_default: str, provider_contact_default: str, provider_contact_phone_default: int, provider_category_default: list, provider_activity_default: list, lic_amb_path_default: str, rut_path_default: str, ccio_path_default: str, other_docs_path_default: str):
    
    # Download section (outside form)
    with st.expander("📥 Descargar documentos actuales", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Licencia ambiental**")
            if lic_amb_path_default and os.path.exists(lic_amb_path_default):
                with open(lic_amb_path_default, "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar",
                        data=file,
                        file_name=os.path.basename(lic_amb_path_default),
                        mime="application/octet-stream",
                        key="download_lic_amb"
                    )
            else:
                st.caption("No hay archivo actual")
            
            st.markdown("**RUT**")
            if rut_path_default and os.path.exists(rut_path_default):
                with open(rut_path_default, "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar",
                        data=file,
                        file_name=os.path.basename(rut_path_default),
                        mime="application/octet-stream",
                        key="download_rut"
                    )
            else:
                st.caption("No hay archivo actual")
            
        with col2:
            st.markdown("**Cámara de comercio**")
            if ccio_path_default and os.path.exists(ccio_path_default):
                with open(ccio_path_default, "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar",
                        data=file,
                        file_name=os.path.basename(ccio_path_default),
                        mime="application/octet-stream",
                        key="download_ccio"
                    )
            else:
                st.caption("No hay archivo actual")
            
            st.markdown("**Otros documentos**")
            if other_docs_path_default:
                # Handle comma-separated paths for multiple files
                other_docs_list = [p.strip() for p in other_docs_path_default.split(",") if p.strip()]
                if other_docs_list:
                    for idx, doc_path in enumerate(other_docs_list):
                        if os.path.exists(doc_path):
                            with open(doc_path, "rb") as file:
                                st.download_button(
                                    label=f"⬇️ Descargar {os.path.basename(doc_path)}",
                                    data=file,
                                    file_name=os.path.basename(doc_path),
                                    mime="application/octet-stream",
                                    key=f"download_other_docs_{idx}"
                                )
                else:
                    st.caption("No hay archivos actuales")
            else:
                st.caption("No hay archivos actuales")
    
    st.divider()
    
    # Form section
    update_form = st.form("update_provider_form")
    with update_form:
        with st.expander("Instrucciones"):
            st.markdown(
                """ 
                - Actualiza la información del proveedor según sea necesario.
                - Usa el expander de arriba para descargar los documentos actuales.
                - Sube nuevos archivos si deseas reemplazar los existentes.
                - Presiona el botón para actualizar el proveedor.
                """
            )
        col1, col2 = st.columns(2)
        with col1:
            provider_name = st.text_input("Nombre del proveedor", value=provider_name_default)
            provider_nit = st.number_input("NIT del proveedor", step=1, format="%d", value=provider_nit_default)
            provider_email = st.text_input("Correo electrónico del proveedor", value=provider_email_default)
            provider_contact = st.text_input("Contacto", value=provider_contact_default)

        with col2:
            provider_contact_phone = st.number_input("Teléfono", step=1, format="%d", value=provider_contact_phone_default)
            provider_category = st.multiselect(
                "Tipos de residuos",
                options=get_enum_values("residue_type"),
                default=provider_category_default
            )
            provider_auth_activities = st.multiselect(
                "Actividades autorizadas",
                options=get_enum_values("activities_performed"),
                default=provider_activity_default
            )
        
        st.divider()
        st.subheader("📄 Reemplazar documentos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lic_amb_file = st.file_uploader("Subir nueva Licencia ambiental", type=["pdf", "jpg", "png"], key="upload_lic_amb")
            rut_file = st.file_uploader("Subir nuevo RUT", type=["pdf", "jpg", "png"], key="upload_rut")
            
        with col2:
            ccio_file = st.file_uploader("Subir nueva Cámara de comercio", type=["pdf", "jpg", "png"], key="upload_ccio")
            other_docs_files = st.file_uploader("Subir nuevos Otros documentos (múltiples permitidos)", type=["pdf", "jpg", "png"], accept_multiple_files=True, key="upload_other_docs")
        
        st.divider()
        submitted = st.form_submit_button("Actualizar proveedor")
        if submitted:
            now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
            
            # Keep existing paths by default
            lic_amb_path = lic_amb_path_default
            rut_path = rut_path_default
            ccio_path = ccio_path_default
            other_docs_path = other_docs_path_default
            
            # Update paths and save new files if uploaded
            if lic_amb_file:
                lic_amb_path = path_file(provider_nit, provider_name, "lic_amb", lic_amb_file)
                save_file(lic_amb_file, lic_amb_path)
            
            if rut_file:
                rut_path = path_file(provider_nit, provider_name, "rut", rut_file)
                save_file(rut_file, rut_path)
            
            if ccio_file:
                ccio_path = path_file(provider_nit, provider_name, "ccio", ccio_file)
                save_file(ccio_file, ccio_path)
            
            # Handle multiple other_docs files
            if other_docs_files:
                # Delete old other_docs files from storage
                if other_docs_path_default:
                    old_docs_list = [p.strip() for p in other_docs_path_default.split(",") if p.strip()]
                    for old_path in old_docs_list:
                        if old_path and os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except Exception as del_err:
                                print(f"Warning: Could not delete old file {old_path}: {del_err}")
                
                # Save new other_docs files
                other_docs_paths = path_files_multiple(provider_nit, provider_name, "other_docs", other_docs_files)
                other_docs_path = ",".join(other_docs_paths) if other_docs_paths else ""
                for file, path in zip(other_docs_files, other_docs_paths):
                    save_file(file, path)
            
            update_provider(id, provider_name, provider_nit, provider_email, provider_contact, provider_contact_phone, provider_category, provider_auth_activities, lic_amb_path, rut_path, ccio_path, other_docs_path, now)     

def select_provider(provider_id: int):
    try:
        provider = supabase.table("providers").select(
            "provider_name, provider_nit, provider_email, provider_contact, provider_contact_phone, provider_category, provider_activity, lic_amb_path, rut_path, ccio_path, other_docs_path"
        ).eq("id", provider_id).execute()
        return provider.data[0] if provider.data else None
    except Exception as e:
        st.error(f"Error seleccionando proveedor: {e}")
        return None

def create_provider_button():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Crear nuevo proveedor", width="stretch"):
            create_provider_dialog()

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
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
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
    try:
        return f"uploads/{provider_nit}_{provider_name}_{file_name}.{upload_file.type.split('/')[-1]}"
    except Exception as e:
        st.error(f"Error generando ruta de archivo: {e}")

def path_files_multiple(provider_nit, provider_name, file_name_prefix, upload_files) -> list:
    """Generate paths for multiple files."""
    try:
        paths = []
        for idx, upload_file in enumerate(upload_files):
            ext = upload_file.type.split('/')[-1]
            path = f"uploads/{provider_nit}_{provider_name}_{file_name_prefix}_{idx+1}.{ext}"
            paths.append(path)
        return paths
    except Exception as e:
        st.error(f"Error generando rutas de archivos: {e}")
        return []

def save_file(file_uploader, file_path) -> str:
    try:
        with open(file_path, mode='wb') as w:
            w.write(file_uploader.getvalue())
        return file_path
    except Exception as e:
        st.error(f"Error guardando archivo: {e}")

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching enum values: {e}")

@st.dialog("Crear proveedor", width="large")
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
        col1, col2 = st.columns(2)
        with col1:
            provider_name = st.text_input("Nombre del proveedor")
            provider_nit = st.number_input("NIT del proveedor", step=1, format="%d")
            provider_email = st.text_input("Correo electrónico del proveedor")
            provider_contact = st.text_input("Contacto")

        with col2:
            provider_contact_phone = st.number_input("Teléfono", step=1, format="%d")
            provider_category = st.multiselect(
                "Tipos de residuos",
                options=get_enum_values("residue_type")
            )
            provider_auth_activities = st.multiselect(
                "Actividades autorizadas",
                options=get_enum_values("activities_performed")
            )
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            lic_amb_file = st.file_uploader("Licencia ambiental", type=["pdf", "jpg", "png"])
            rut_file = st.file_uploader("RUT", type=["pdf", "jpg", "png"])
        with col2:
            ccio_file = st.file_uploader("Cámara de comercio", type=["pdf", "jpg", "png"])
            other_docs_files = st.file_uploader("Otros documentos (múltiples archivos permitidos)", type=["pdf", "jpg", "png"], accept_multiple_files=True)    
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            username = "user1"
            # Validate required file uploads
            missing = []
            if not lic_amb_file:
                missing.append("Licencia ambiental")
            if not rut_file:
                missing.append("RUT")
            if not ccio_file:
                missing.append("Cámara de comercio")

            if missing:
                st.error(f"Faltan documentos obligatorios: {', '.join(missing)}")
                return

            # Build file paths safely
            lic_amb_path = path_file(provider_nit, provider_name, "lic_amb", lic_amb_file)
            rut_path = path_file(provider_nit, provider_name, "rut", rut_file)
            ccio_path = path_file(provider_nit, provider_name, "ccio", ccio_file)
            
            # Handle multiple other_docs files
            other_docs_paths = []
            if other_docs_files:
                other_docs_paths = path_files_multiple(provider_nit, provider_name, "other_docs", other_docs_files)
            other_docs_path = ",".join(other_docs_paths) if other_docs_paths else ""

            # Persist provider record
            try:
                result = create_provider(
                    username,
                    provider_name,
                    provider_nit,
                    provider_email,
                    provider_contact,
                    provider_contact_phone,
                    provider_category,
                    provider_auth_activities,
                    lic_amb_path,
                    rut_path,
                    ccio_path,
                    other_docs_path,
                )
                
                # Only save files if database insertion succeeded
                if result:
                    save_file(lic_amb_file, lic_amb_path)
                    save_file(rut_file, rut_path)
                    save_file(ccio_file, ccio_path)

                    # Save multiple other_docs files
                    if other_docs_files and other_docs_paths:
                        for file, path in zip(other_docs_files, other_docs_paths):
                            save_file(file, path)

                    st.toast("✅ Proveedor creado exitosamente! ")
                    time.sleep(2)
                    st.rerun()
            except Exception as e:
                st.toast(f"❌ Error al crear proveedor: {e}")

def display_providers_table(providers_data):
    try:
        rows = pd.DataFrame(providers_data)
        rows.set_index("id", inplace=True)
        st.dataframe(
            rows,
            width="stretch",
            column_config={
                "id": "ID del proveedor",
                "provider_name": "Nombre del proveedor",
                "created_at": st.column_config.DateColumn(
                    "Creado en",
                    format="distance"
                ),
                "updated_at": st.column_config.DateColumn(
                    "Actualizado en",
                    format="distance"
                )
            }
        )
    except Exception as e:
        st.write(f"No hay datos disponibles") 

def display_all_providers_table(providers_data):
    try:
        rows = pd.DataFrame(providers_data)
        rows = rows[["id", "provider_name","provider_category", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False
        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","provider_name", "provider_category", "created_at", "updated_at"],
            column_config={
                "id": "ID",
                "provider_name": "Nombre del proveedor",
                "provider_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_type"),
                    color=["blue", "green", "orange", "red", "purple", "brown", "gray"]
                ),
                "created_at": st.column_config.DateColumn(
                    "Creado en",
                    format="distance"
                ),
                "updated_at": st.column_config.DateColumn(
                    "Actualizado en",
                    format="distance"
                )
            }
        )
        selected_count = displayed_table.Seleccionar.sum()
        col1, col2 = st.columns(2)
        if selected_count > 0 and selected_count < 2:
            with col1:    
                if st.button("🔁 Editar solicitud", width="stretch"):
                    default_options = select_provider(displayed_table[displayed_table["Seleccionar"]].index.tolist()[0])
                    update_provider_form(
                        id=displayed_table[displayed_table["Seleccionar"]].index.tolist()[0],
                        provider_name_default=default_options["provider_name"],
                        provider_nit_default=default_options["provider_nit"],
                        provider_email_default=default_options["provider_email"],
                        provider_contact_default=default_options["provider_contact"],
                        provider_contact_phone_default=default_options["provider_contact_phone"],
                        provider_category_default=default_options["provider_category"],
                        provider_activity_default=default_options["provider_activity"],
                        lic_amb_path_default=default_options["lic_amb_path"],
                        rut_path_default=default_options["rut_path"],
                        ccio_path_default=default_options["ccio_path"],
                        other_docs_path_default=default_options["other_docs_path"]
                    )
        if selected_count > 0 or selected_count >= 2:
            with col2:
                if st.button("🗑️ Eliminar solicitudes", width="stretch"):
                    confirm_delete_dialog(displayed_table[displayed_table["Seleccionar"]].index.tolist())   
    except Exception as e:
        st.write(f"No hay proveedores disponibles aun")


### Page layout and logic ###
mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:
    
    st.page_link("./pages/nav4.py", label="⬅️ Atrás", use_container_width=True)
    mc.logout_and_home()

    ### Formulario de solicitud de servicio ###
    st.subheader("📋 Proveedores")

    create_provider_button()

    st.divider()

    st.subheader("📋 Gestión de proveedores")

    display_all_providers_table(list_all_providers(200))


else:
    st.switch_page("./pages/login_home.py")