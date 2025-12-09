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
def deactivate_provider(provider_ids: list):
    """Deactivate one or more providers by their IDs and remove their files."""
    try:
        # deleted_files = 0
        for provider_id in provider_ids:
            # # Fetch file paths to delete files from disk
            # provider = supabase.table("providers").select(
            #     "lic_amb_path, rut_path, ccio_path, other_docs_path, certificado_bancario_path"
            # ).eq("id", provider_id).execute()

            # if provider.data:
            #     # Handle multiple files for lic_amb and other_docs (comma-separated)
            #     lic_amb_paths = provider.data[0].get("lic_amb_path", "")
            #     other_docs_paths = provider.data[0].get("other_docs_path", "")
            #     rut_path = provider.data[0].get("rut_path", "")
            #     ccio_path = provider.data[0].get("ccio_path", "")
            #     certificado_bancario_path = provider.data[0].get("certificado_bancario_path", "")

            #     file_paths = []
            #     if lic_amb_paths:
            #         file_paths.extend([p.strip() for p in lic_amb_paths.split(",") if p.strip()])
            #     if other_docs_paths:
            #         file_paths.extend([p.strip() for p in other_docs_paths.split(",") if p.strip()])
            #     if rut_path:
            #         file_paths.append(rut_path.strip())
            #     if ccio_path:
            #         file_paths.append(ccio_path.strip())
            #     if certificado_bancario_path:
            #         file_paths.append(certificado_bancario_path.strip())

            #     # Remove files from disk if they exist
            #     for file_path in file_paths:
            #         if file_path and os.path.exists(file_path):
            #             try:
            #                 os.remove(file_path)
            #                 deleted_files += 1
            #             except Exception as file_err:
            #                 print(f"Warning: Could not delete file {file_path}: {file_err}")

            # Delete provider from database
            supabase.table("providers").update({"provider_is_active": False}).eq("id", provider_id).execute()

        st.toast(f"✅ {len(provider_ids)} proveedores eliminados exitosamente")
        return True

    except Exception as e:
        st.error(f"Error eliminando proveedor(es): {e.message}")
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
            if deactivate_provider(provider_ids):
                time.sleep(1)
                st.rerun()

def update_provider(
        provider_id: int,
        provider_name: str, 
        provider_nit: int, 
        provider_email: str, 
        provider_contact: str, 
        provider_contact_phone: int, 
        provider_website: str,
        provider_category: list,
        provider_activity: list, 
        lic_amb_path: str, 
        rut_path: str, 
        ccio_path: str, 
        other_docs_path: str,
        certificado_bancario_path: str,
        updated_at: str
    ):
    try:
        request = supabase.table("providers").update({
            "provider_name": provider_name,
            # "provider_nit": provider_nit, # NIT should not be changed as it may require to rename files associated with the provider
            "provider_email": provider_email,
            "provider_contact": provider_contact,
            "provider_contact_phone": provider_contact_phone,
            "provider_website": provider_website,
            "provider_category": provider_category,
            "provider_activity": provider_activity,
            "lic_amb_path": lic_amb_path,
            "rut_path": rut_path,
            "ccio_path": ccio_path,
            "other_docs_path": other_docs_path,
            "certificado_bancario_path": certificado_bancario_path,
            "updated_at": updated_at
        }).eq("id", provider_id).execute()
        st.toast("✅ Proveedor actualizado exitosamente")
        st.rerun()
        return request

    except Exception as e:
        st.error(f"Error actualizando proveedor: {e.message}")

@st.dialog("Actualizar proveedor", width="large")
def update_provider_form(id: int,provider_name_default: str, provider_nit_default: int, provider_email_default: str, provider_contact_default: str, provider_contact_phone_default: int, provider_website_default: str, provider_category_default: list, provider_activity_default: list, lic_amb_path_default: str, rut_path_default: str, ccio_path_default: str, other_docs_path_default: str, certificado_bancario_path_default: str = ""):    
    # Form section
    update_form = st.form("update_provider_form")
    with update_form:
        with st.expander("Instrucciones"):
            st.markdown(
                """ 
                - Actualiza la información del proveedor según sea necesario.
                - Usa el desplegable de arriba para descargar los documentos actuales.
                - Sube nuevos archivos si deseas reemplazar los existentes.
                - Presiona el botón para actualizar el proveedor.
                """
            )
        col1, col2 = st.columns(2)
        with col1:
            provider_name = st.text_input("Nombre del proveedor", value=provider_name_default)
            provider_nit = st.number_input("NIT del proveedor", step=1, format="%d", value=provider_nit_default, disabled=True)
            provider_email = st.text_input("Correo electrónico del proveedor", value=provider_email_default)
            provider_contact = st.text_input("Contacto", value=provider_contact_default)

        with col2:
            provider_contact_phone = st.number_input("Teléfono", step=1, format="%d", value=provider_contact_phone_default)
            provider_website = st.text_input("Sitio web (opcional)", value=provider_website_default, placeholder="https://ejemplo.com")
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
            lic_amb_files = st.file_uploader("Subir nueva Licencia ambiental (múltiples permitidos)", type=["pdf", "jpg", "png"], accept_multiple_files=True, key="upload_lic_amb")
            rut_file = st.file_uploader("Subir nuevo RUT", type=["pdf", "jpg", "png"], key="upload_rut")
            
        with col2:
            ccio_file = st.file_uploader("Subir nueva Cámara de comercio", type=["pdf", "jpg", "png"], key="upload_ccio")
            other_docs_files = st.file_uploader("Subir nuevos Otros documentos (múltiples permitidos)", type=["pdf", "jpg", "png"], accept_multiple_files=True, key="upload_other_docs")
            certificado_bancario_file = st.file_uploader("Subir nuevo Certificado bancario (opcional)", type=["pdf", "jpg", "png"], key="upload_certificado_bancario")
        
        st.divider()
        submitted = st.form_submit_button("Actualizar proveedor")
        if submitted:
            now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
            
            # Keep existing paths by default
            lic_amb_path = lic_amb_path_default
            rut_path = rut_path_default
            ccio_path = ccio_path_default
            other_docs_path = other_docs_path_default
            certificado_bancario_path = certificado_bancario_path_default
            
            # Update paths and save new files if uploaded
            if lic_amb_files:
                # Save new lic_amb files and append to existing paths
                new_lic_amb_paths = path_files_multiple(provider_nit, "lic_amb", lic_amb_files)
                
                # Append to existing paths instead of replacing
                if lic_amb_path_default:
                    existing_paths = [p.strip() for p in lic_amb_path_default.split(",") if p.strip()]
                    all_paths = existing_paths + new_lic_amb_paths
                else:
                    all_paths = new_lic_amb_paths
                
                lic_amb_path = ",".join(all_paths) if all_paths else ""
                for file, path in zip(lic_amb_files, new_lic_amb_paths):
                    save_file(file, path)
            
            if rut_file:
                rut_path = path_file(provider_nit, "rut", rut_file)
                save_file(rut_file, rut_path)
            
            if ccio_file:
                ccio_path = path_file(provider_nit, "ccio", ccio_file)
                save_file(ccio_file, ccio_path)
            
            # Handle multiple other_docs files
            if other_docs_files:
                # Save new other_docs files and append to existing paths
                new_other_docs_paths = path_files_multiple(provider_nit, "other_docs", other_docs_files)
                
                # Append to existing paths instead of replacing
                if other_docs_path_default:
                    existing_paths = [p.strip() for p in other_docs_path_default.split(",") if p.strip()]
                    all_paths = existing_paths + new_other_docs_paths
                else:
                    all_paths = new_other_docs_paths
                
                other_docs_path = ",".join(all_paths) if all_paths else ""
                for file, path in zip(other_docs_files, new_other_docs_paths):
                    save_file(file, path)

            if certificado_bancario_file:
                certificado_bancario_path = path_file(provider_nit, "certificado_bancario", certificado_bancario_file)
                save_file(certificado_bancario_file, certificado_bancario_path)
            
            update_provider(id, provider_name, provider_nit, provider_email, provider_contact, provider_contact_phone, provider_website, provider_category, provider_auth_activities, lic_amb_path, rut_path, ccio_path, other_docs_path, certificado_bancario_path, now)     

def select_provider(provider_id: int):
    try:
        provider = supabase.table("providers").select(
            "provider_name, provider_nit, provider_email, provider_contact, provider_contact_phone, provider_website, provider_category, provider_activity, lic_amb_path, rut_path, ccio_path, other_docs_path, certificado_bancario_path, provider_website, updated_at"
        ).eq("id", provider_id).execute()
        return provider.data[0] if provider.data else None
    except Exception as e:
        st.error(f"Error seleccionando proveedor: {e.message}")
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
        provider_website: str,
        provider_category: list,
        provider_activity: list, 
        lic_amb_path: str, 
        rut_path: str, 
        ccio_path: str, 
        other_docs_path: str,
        certificado_bancario_path: str,
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
            "provider_website": provider_website,
            "provider_category": provider_category,
            "provider_activity": provider_activity,
            "lic_amb_path": lic_amb_path,
            "rut_path": rut_path,
            "ccio_path": ccio_path,
            "other_docs_path": other_docs_path,
            "certificado_bancario_path": certificado_bancario_path,
            "created_at": now,
            "updated_at": now
        }).execute()
        return request

    except Exception as e:
        st.error(f"Error creando proveedor: {e.message}")

def list_all_providers(limit=200):
    try:
        providers = supabase.table("providers").select("*").order("id", desc=True).limit(limit).execute()
        return providers.data
    except Exception as e:
        st.error(f"Error fetching providers: {e.message}")
        return []

def format_date(date_str: str) -> str:
    # When displaying dates from Supabase, parse and format them
    # Parse ISO format string to datetime
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    # Format as desired
    return date_obj.strftime("%Y %B  %d %H:%M %Z")

def path_file(provider_nit, file_name, upload_file) -> str:
    try:
        ext = upload_file.type.split('/')[-1]
        return f"uploads/{provider_nit}_{file_name}.{ext}"
    except Exception as e:
        st.error(f"Error generando ruta de archivo: {e.message}")

def path_files_multiple(provider_nit, file_name_prefix, upload_files) -> list:
    """Generate paths for multiple files."""
    try:
        paths = []
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        for idx, upload_file in enumerate(upload_files):
            ext = upload_file.type.split('/')[-1]
            path = f"uploads/{provider_nit}_{file_name_prefix}_{timestamp}_{idx+1}.{ext}"
            paths.append(path)
        return paths
    except Exception as e:
        st.error(f"Error generando rutas de archivos: {e.message}")
        return []

def save_file(file_uploader, file_path) -> str:
    try:
        with open(file_path, mode='wb') as w:
            w.write(file_uploader.getvalue())
        return file_path
    except Exception as e:
        st.error(f"Error guardando archivo: {e.message}")

def get_enum_values(enum_name: str):
    try:
        result = supabase.rpc('get_types', {'enum_type': f'{enum_name}'}).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching enum values: {e.message}")

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
            provider_website = st.text_input("Sitio web (opcional)", placeholder="https://ejemplo.com")
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
            lic_amb_files = st.file_uploader("Licencia ambiental (múltiples archivos permitidos)", type=["pdf", "jpg", "png"], accept_multiple_files=True)
            rut_file = st.file_uploader("RUT", type=["pdf", "jpg", "png"])
        with col2:
            ccio_file = st.file_uploader("Cámara de comercio", type=["pdf", "jpg", "png"])
            other_docs_files = st.file_uploader("Otros documentos (múltiples archivos permitidos)", type=["pdf", "jpg", "png"], accept_multiple_files=True)
            certificado_bancario_file = st.file_uploader("Certificado bancario (opcional)", type=["pdf", "jpg", "png"])    
        submitted = st.form_submit_button("Enviar solicitud")
        if submitted:
            username = f"{ss["name"]}"
            # Validate required file uploads
            missing = []
            if not lic_amb_files:
                missing.append("Licencia ambiental")
            if not rut_file:
                missing.append("RUT")
            if not ccio_file:
                missing.append("Cámara de comercio")

            if missing:
                st.error(f"Faltan documentos obligatorios: {', '.join(missing)}")
                return

            # Build file paths safely
            lic_amb_paths = path_files_multiple(provider_nit, "lic_amb", lic_amb_files)
            lic_amb_path = ",".join(lic_amb_paths) if lic_amb_paths else ""
            rut_path = path_file(provider_nit, "rut", rut_file)
            ccio_path = path_file(provider_nit, "ccio", ccio_file)
            
            # Handle multiple other_docs files
            other_docs_paths = []
            if other_docs_files:
                other_docs_paths = path_files_multiple(provider_nit, "other_docs", other_docs_files)
            other_docs_path = ",".join(other_docs_paths) if other_docs_paths else ""
            certificado_bancario_path = ""
            if certificado_bancario_file:
                certificado_bancario_path = path_file(provider_nit, "certificado_bancario", certificado_bancario_file)

            # Persist provider record
            try:
                result = create_provider(
                    username,
                    provider_name,
                    provider_nit,
                    provider_email,
                    provider_contact,
                    provider_contact_phone,
                    provider_website,
                    provider_category,
                    provider_auth_activities,
                    lic_amb_path,
                    rut_path,
                    ccio_path,
                    other_docs_path,
                    certificado_bancario_path,
                )
                
                # Only save files if database insertion succeeded
                if result:
                    # Save multiple lic_amb files
                    if lic_amb_files and lic_amb_paths:
                        for file, path in zip(lic_amb_files, lic_amb_paths):
                            save_file(file, path)
                    
                    save_file(rut_file, rut_path)
                    save_file(ccio_file, ccio_path)

                    # Save multiple other_docs files
                    if other_docs_files and other_docs_paths:
                        for file, path in zip(other_docs_files, other_docs_paths):
                            save_file(file, path)

                    # Save certificado bancario if provided
                    if certificado_bancario_file:
                        save_file(certificado_bancario_file, certificado_bancario_path)

                    st.toast("✅ Proveedor creado exitosamente! ")
                    time.sleep(2)
                    st.rerun()
            except Exception as e:
                st.toast(f"❌ Error al crear proveedor: {e.message}")
                
@st.dialog("📋 Detalle del proveedor", width="large")
def provider_detail_view(provider_id: int):
    """Display detailed view of a provider with all information and downloadable files."""
    try:
        provider = select_provider(provider_id)
        if not provider:
            st.error("No se pudo cargar la información del proveedor")
            return
        
        # Provider information and services section
        with st.expander("ℹ️ Información general y servicios", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Nombre:** {provider.get('provider_name', 'N/A')}")
                # Estado segun año de actualización
                updated_at = provider.get('updated_at')
                status_label = None
                if updated_at:
                    try:
                        dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        status_label = "Actualizado" if dt.year == datetime.now().year else "Vencido"
                    except Exception:
                        status_label = None
                if status_label:
                    color = "green" if status_label == "Actualizado" else "red"
                    st.markdown(f"**Estado:** :{color}-badge[{status_label}]")
                else:
                    st.markdown("**Estado:** No disponible")
                st.markdown(f"**NIT:** {provider.get('provider_nit', 'N/A')}")
                st.markdown(f"**Email:** {provider.get('provider_email', 'N/A')}")
            
            with col2:
                st.markdown(f"**Contacto:** {provider.get('provider_contact', 'N/A')}")
                st.markdown(f"**Teléfono:** {provider.get('provider_contact_phone', 'N/A')}")
                website = provider.get('provider_website', '')
                if website:
                    st.markdown(f"**Sitio web:** [{website}]({website})")
                else:
                    st.markdown("**Sitio web:** No especificado")

                    
            with col1:
                categories = provider.get('provider_category', [])
                if categories:
                    # Color mapping to match dataframe
                    color_map = ["blue", "green", "orange", "red", "violet", "orange", "gray"]
                    badges = " ".join([f":{color_map[idx % len(color_map)]}-badge[{cat}]" for idx, cat in enumerate(categories)])
                    st.markdown(f"**Tipos de residuos:** {badges}")
                else:
                    st.markdown("**Tipos de residuos:** No especificado")
            
            with col2:
                activities = provider.get('provider_activity', [])
                if activities:
                    st.markdown("**Actividades autorizadas:** " + ", ".join(activities))
                else:
                    st.markdown("**Actividades autorizadas:** No especificado")
        
        # Documents section with inline PDF viewers
        with st.expander("📄 Documentos soporte", expanded=False):
            # Licencia ambiental
            with st.expander("📄 Licencia ambiental", expanded=False):
                lic_amb_path = provider.get('lic_amb_path', '')
                if lic_amb_path:
                    lic_amb_list = [p.strip() for p in lic_amb_path.split(",") if p.strip()]
                    if lic_amb_list:
                        has_files = False
                        for idx, doc_path in enumerate(lic_amb_list):
                            if os.path.exists(doc_path):
                                has_files = True
                                with st.expander(f"📄 Ver Licencia ambiental {idx+1}"):
                                    try:
                                        with open(doc_path, "rb") as pdf_file:
                                            pdf_data = pdf_file.read()
                                            st.pdf(pdf_data, key=f"view_lic_amb_pdf_{idx}")
                                    except Exception as e:
                                        st.error(f"Error cargando PDF: {e.message}")
                        if not has_files:
                            st.caption("No hay archivos disponibles")
                    else:
                        st.caption("No hay archivos disponibles")
                else:
                    st.caption("No hay archivos disponibles")
    
            # RUT
            st.markdown("**RUT**")
            rut_path = provider.get('rut_path', '')
            if rut_path and os.path.exists(rut_path):
                with st.expander("📄 Ver RUT"):
                    try:
                        with open(rut_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                            st.pdf(pdf_data, key="view_rut_pdf")
                    except Exception as e:
                        st.error(f"Error cargando PDF: {e.message}")
            else:
                st.caption("No hay archivo disponible")
            
            # Cámara de comercio
            st.markdown("**Cámara de comercio**")
            ccio_path = provider.get('ccio_path', '')
            if ccio_path and os.path.exists(ccio_path):
                with st.expander("📄 Ver Cámara de comercio"):
                    try:
                        with open(ccio_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                            st.pdf(pdf_data, key="view_ccio_pdf")
                    except Exception as e:
                        st.error(f"Error cargando PDF: {e.message}")
            else:
                st.caption("No hay archivo disponible")
            
            # Certificado bancario
            st.markdown("**Certificado bancario**")
            certificado_bancario_path = provider.get('certificado_bancario_path', '')
            if certificado_bancario_path and os.path.exists(certificado_bancario_path):
                with st.expander("📄 Ver Certificado bancario"):
                    try:
                        with open(certificado_bancario_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                            st.pdf(pdf_data, key="view_certificado_bancario_pdf")
                    except Exception as e:
                        st.error(f"Error cargando PDF: {e.message}")
            else:
                st.caption("No hay archivo disponible")

            # Otros documentos
            with st.expander("📄 Otros documentos", expanded=False):
                other_docs_path = provider.get('other_docs_path', '')
                if other_docs_path:
                    other_docs_list = [p.strip() for p in other_docs_path.split(",") if p.strip()]
                    if other_docs_list:
                        has_files = False
                        for idx, doc_path in enumerate(other_docs_list):
                            if os.path.exists(doc_path):
                                has_files = True
                                with st.expander(f"📄 Ver Documento {idx+1}"):
                                    try:
                                        with open(doc_path, "rb") as pdf_file:
                                            pdf_data = pdf_file.read()
                                            st.pdf(pdf_data, key=f"view_other_docs_pdf_{idx}")
                                    except Exception as e:
                                        st.error(f"Error cargando PDF: {e.message}")
                        if not has_files:
                            st.caption("No hay archivos disponibles")
                    else:
                        st.caption("No hay archivos disponibles")
                else:
                    st.caption("No hay archivos disponibles")
    
    except Exception as e:
        st.error(f"Error cargando detalles del proveedor: {e.message}")

def display_all_providers_table(providers_data):
    try:
        rows = pd.DataFrame(providers_data)
        rows = rows[(rows["provider_is_active"] == True)]
        if rows.empty:
            st.info("📭 No hay proveedores disponibles aun.")
            return
        rows = rows[["id", "provider_name", "provider_nit", "provider_category", "created_at", "updated_at"]]
        rows["created_at"] = pd.to_datetime(rows["created_at"])
        rows["updated_at"] = pd.to_datetime(rows["updated_at"])
        # Add status column based on current year vs updated_at year
        current_year = pd.Timestamp.now().year
        rows["Estado"] = rows["updated_at"].dt.year.apply(lambda y: "Actualizado" if y == current_year else "Vencido")
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False
        displayed_table = st.data_editor(
            rows,
            width="stretch",
            disabled=["id","provider_name", "provider_nit", "provider_category", "created_at", "updated_at", "Estado"],
            column_config={
                "id": "ID",
                "provider_is_active": "Activo",
                "provider_name": "Nombre del proveedor",
                "provider_nit": "NIT del proveedor",
                "provider_category": st.column_config.MultiselectColumn(
                    "Categorías de residuos",
                    options=get_enum_values("residue_type"),
                    color=["blue", "green", "orange", "red", "purple", "brown", "gray"]
                ),
                "created_at": st.column_config.DateColumn(
                    "Fecha de creación",
                    format="DD/MM/YY HH:mm"
                ),
                "updated_at": st.column_config.DateColumn(
                    "Última modificación",
                    format="DD/MM/YY HH:mm"
                ),
                "Estado": st.column_config.MultiselectColumn(
                    "Estado",
                    options=["Actualizado", "Vencido"],
                    color=["green", "red"]
                )
            }
        )
        selected_count = displayed_table.Seleccionar.sum()
        col1, col2, col3 = st.columns(3)
        if selected_count > 0 and selected_count < 2:
            selected_id = displayed_table[displayed_table["Seleccionar"]].index.tolist()[0]
            
            with col1:
                if st.button("👁️ Consultar", width="stretch"):
                    provider_detail_view(selected_id)
            
            with col2:    
                if st.button("🔁 Editar proveedor", width="stretch"):
                    default_options = select_provider(selected_id)
                    update_provider_form(
                        id=selected_id,
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
                        other_docs_path_default=default_options["other_docs_path"],
                        provider_website_default=default_options["provider_website"]
                    )
        if selected_count > 0 or selected_count >= 2:
            with col3:
                if st.button("🗑️ Eliminar proveedor/es", width="stretch"):
                    confirm_delete_dialog(displayed_table[displayed_table["Seleccionar"]].index.tolist())   
    except Exception as e:
        st.write(f"No hay proveedores disponibles aun")

# @st.dialog("PDF Viewer", width="large")
# def pdf_viewer_dialog(pdf_path: str):
#     """Dialog to display a PDF file."""
#     try:
#         with open(pdf_path, "rb") as pdf_file:
#             PDFbyte = pdf_file.read()
#             st.pdf(PDFbyte)
#     except Exception as e:
#         st.error(f"Error loading PDF: {e.message}")

### Page layout and logic ###
mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:

    st.page_link("./pages/residuos_peligrosos.py", label="⬅️ Atrás", use_container_width=True)
    mc.logout_and_home('./pages/residuos_peligrosos.py')
    
    ### Formulario de solicitud de servicio ###
    st.subheader("📋 Gestión de proveedores")


    create_provider_button()

    st.divider()

    display_all_providers_table(list_all_providers(200))


else:
    st.switch_page("./pages/login_home.py")