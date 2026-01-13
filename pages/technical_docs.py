"""
Technical Documents Management Page
Allows users to upload, view, update, and manage technical documents.
"""

### Minimal import for a Streamlit page ###
import streamlit as st
from streamlit import session_state as ss
import modules.common as mc

### Page specific imports ###
from modules.tech_docs import (
    add_document, update_document, delete_document,
    get_all_documents, get_document_by_id, get_document_file,
    search_documents, get_storage_stats
)
from datetime import datetime
import pandas as pd


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_datetime(iso_datetime: str) -> str:
    """Format ISO datetime string to readable format."""
    try:
        dt = datetime.fromisoformat(iso_datetime)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_datetime


def upload_document_section():
    """Section for uploading new documents."""
    st.subheader("📤 Subir Nuevo Documento")
    
    with st.form("upload_form", clear_on_submit=True):
        doc_name = st.text_input(
            "Nombre del Documento*",
            placeholder="Ej: Manual de Seguridad 2024",
            help="Nombre descriptivo para identificar el documento"
        )
        
        description = st.text_area(
            "Descripción",
            placeholder="Descripción breve del contenido del documento (opcional)",
            help="Información adicional sobre el documento"
        )
        
        # Year and Month inputs
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input(
                "Año*",
                min_value=2000,
                max_value=2100,
                value=datetime.now().year,
                help="Año del documento"
            )
        with col2:
            month = st.selectbox(
                "Mes*",
                options=list(range(1, 13)),
                format_func=lambda x: f"{x:02d}",
                index=datetime.now().month - 1,
                help="Mes del documento"
            )
        
        uploaded_file = st.file_uploader(
            "Seleccionar Archivo*",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'],
            help="Formatos permitidos: PDF, Word, Excel, TXT, Imágenes"
        )
        
        submitted = st.form_submit_button("⬆️ Subir Documento", use_container_width=True)
        
        if submitted:
            if not doc_name:
                st.error("⚠️ Por favor ingrese un nombre para el documento.")
            elif not uploaded_file:
                st.error("⚠️ Por favor seleccione un archivo para subir.")
            else:
                # Get file bytes
                file_bytes = uploaded_file.read()
                username = ss.get('username', 'unknown')
                
                # Upload document
                success, message = add_document(
                    file_bytes=file_bytes,
                    file_name=uploaded_file.name,
                    document_name=doc_name,
                    uploaded_by=username,
                    description=description,
                    year=int(year),
                    month=int(month)
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


def view_documents_section():
    """Section for viewing and managing existing documents."""
    st.subheader("📚 Documentos Técnicos")
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "🔍 Buscar documentos",
            placeholder="Buscar por nombre, descripción o archivo...",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    # Get documents
    if search_query:
        documents = search_documents(search_query)
        if not documents:
            st.info(f"No se encontraron documentos que coincidan con '{search_query}'")
            return
    else:
        documents = get_all_documents()
    
    if not documents:
        st.info("📭 No hay documentos disponibles. Sube tu primer documento arriba.")
        return
    
    # Storage stats
    stats = get_storage_stats()
    st.caption(f"📊 Total: {stats['total_files']} documentos • {stats['total_size_formatted']}")
    
    # Convert to DataFrame
    try:
        rows = pd.DataFrame(documents)
        
        # Format columns for display
        rows["uploaded_at_formatted"] = pd.to_datetime(rows["uploaded_at"]).dt.strftime("%Y-%m-%d %H:%M")
        
        # Select columns to display: Year, Month, Name, Uploaded at
        display_cols = ["id", "year", "month", "name", "uploaded_at_formatted"]
        rows = rows[display_cols]
        
        # Sort by upload date (newest first)
        rows = rows.sort_values("uploaded_at_formatted", ascending=False)
        
        # Set index and add selection column
        rows.set_index("id", inplace=True)
        rows["Seleccionar"] = False
        
        # Display data editor
        displayed_table = st.data_editor(
            rows,
            use_container_width=True,
            disabled=["year", "month", "name", "uploaded_at_formatted"],
            column_config={
                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    help="Selecciona un documento para ver, editar o eliminar",
                    default=False,
                    pinned=True
                ),
                "year": st.column_config.NumberColumn(
                    "Año",
                    help="Año de carga"
                ),
                "month": st.column_config.NumberColumn(
                    "Mes",
                    help="Mes de carga"
                ),
                "name": st.column_config.TextColumn(
                    "Nombre",
                    help="Nombre del documento"
                ),
                "uploaded_at_formatted": st.column_config.TextColumn(
                    "Subido",
                    help="Fecha y hora de carga"
                )
            },
            hide_index=False
        )
        
        # Action buttons based on selection
        selected_count = displayed_table["Seleccionar"].sum()
        selected_ids = displayed_table[displayed_table["Seleccionar"]].index.tolist()
        
        if selected_count > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👁️ Ver Documento", use_container_width=True, disabled=selected_count != 1):
                    if selected_count == 1:
                        view_document(selected_ids[0])
            
            with col2:
                if st.button("✏️ Editar Documento", use_container_width=True, disabled=selected_count != 1):
                    if selected_count == 1:
                        ss[f'editing_{selected_ids[0]}'] = True
                        st.rerun()
            
            with col3:
                if st.button("🗑️ Eliminar Seleccionados", use_container_width=True):
                    ss['deleting_batch'] = selected_ids
                    st.rerun()
        
        # Show edit form if editing
        if selected_count == 1 and ss.get(f'editing_{selected_ids[0]}', False):
            doc = get_document_by_id(selected_ids[0])
            if doc:
                edit_document_form(doc)
        
        # Show delete confirmation if deleting
        if 'deleting_batch' in ss and ss['deleting_batch']:
            delete_batch_confirmation(ss['deleting_batch'])
            
    except Exception as e:
        st.error(f"❌ Error al mostrar documentos: {str(e)}")
        st.info("📭 No hay documentos disponibles")

@st.dialog("Ver Documento", width="wide")
def view_document(doc_id: str):
    """Display document viewer."""
    result = get_document_file(doc_id)
    if not result:
        st.error("❌ No se pudo cargar el documento.")
        return
    
    file_bytes, filename, mime_type = result
    doc = get_document_by_id(doc_id)
    
    # Show document details in a modal
    st.markdown(f"**Archivo:** {filename}")
    st.markdown(f"**Tamaño:** {format_file_size(len(file_bytes))}")
    if doc.get('description'):
        st.markdown(f"**Descripción:** {doc['description']}")
    st.markdown(f"**Subido por:** {doc.get('uploaded_by', 'N/A')}")
    st.markdown(f"**Fecha:** {format_datetime(doc.get('uploaded_at', ''))}")
    
    # Download button
    st.download_button(
        label="⬇️ Descargar Documento",
        data=file_bytes,
        file_name=filename,
        mime=mime_type,
        use_container_width=True
    )
    
    # Display PDF preview if it's a PDF
    if mime_type == 'application/pdf':
        st.divider()
        st.markdown("**Vista Previa:**")
        # Use base64 to display PDF
        import base64
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)


def edit_document_form(doc: dict):
    """Form for editing a document."""
    with st.form(f"edit_form_{doc['id']}"):
        st.markdown("### ✏️ Editar Documento")
        
        new_name = st.text_input(
            "Nombre del Documento",
            value=doc['name'],
            key=f"edit_name_{doc['id']}"
        )
        
        new_description = st.text_area(
            "Descripción",
            value=doc.get('description', ''),
            key=f"edit_desc_{doc['id']}"
        )
        
        st.markdown("**Reemplazar archivo (opcional):**")
        new_file = st.file_uploader(
            "Nuevo Archivo",
            type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'],
            key=f"edit_file_{doc['id']}",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
        with col2:
            cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if save_button:
            file_bytes = None
            file_name = None
            
            if new_file:
                file_bytes = new_file.read()
                file_name = new_file.name
            
            username = ss.get('username', 'unknown')
            success, message = update_document(
                doc_id=doc['id'],
                file_bytes=file_bytes,
                file_name=file_name,
                document_name=new_name if new_name != doc['name'] else None,
                description=new_description if new_description != doc.get('description', '') else None,
                updated_by=username
            )
            
            if success:
                st.success(f"✅ {message}")
                ss[f'editing_{doc["id"]}'] = False
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        if cancel_button:
            ss[f'editing_{doc["id"]}'] = False
            st.rerun()


def delete_document_confirmation(doc: dict):
    """Confirmation dialog for deleting a document."""
    with st.form(f"delete_form_{doc['id']}"):
        st.warning(f"⚠️ ¿Está seguro que desea eliminar el documento **{doc['name']}**?")
        st.caption("Esta acción no se puede deshacer.")
        
        col1, col2 = st.columns(2)
        with col1:
            confirm_button = st.form_submit_button("🗑️ Sí, Eliminar", use_container_width=True)
        with col2:
            cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if confirm_button:
            success, message = delete_document(doc['id'])
            if success:
                st.success(f"✅ {message}")
                ss[f'deleting_{doc["id"]}'] = False
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        if cancel_button:
            ss[f'deleting_{doc["id"]}'] = False
            st.rerun()


@st.dialog("⚠️ Confirmar eliminación")
def delete_batch_confirmation(doc_ids: list):
    """Confirmation dialog for deleting multiple documents."""
    st.warning(f"¿Está seguro que desea eliminar {len(doc_ids)} documento(s)?")
    
    # Show list of documents to be deleted
    st.markdown("**Documentos a eliminar:**")
    for doc_id in doc_ids:
        doc = get_document_by_id(doc_id)
        if doc:
            st.markdown(f"- {doc['name']} ({doc['original_filename']})")
    
    st.error("⚠️ Esta acción no se puede deshacer.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancelar", use_container_width=True, type="secondary"):
            ss['deleting_batch'] = None
            st.rerun()
    with col2:
        if st.button("✅ Confirmar eliminación", use_container_width=True, type="primary"):
            errors = []
            success_count = 0
            
            for doc_id in doc_ids:
                success, message = delete_document(doc_id)
                if success:
                    success_count += 1
                else:
                    errors.append(message)
            
            if success_count > 0:
                st.success(f"✅ {success_count} documento(s) eliminado(s) exitosamente")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            
            ss['deleting_batch'] = None
            st.rerun()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

### Main page code ###
if ss["authentication_status"]:
    mc.logout_and_home('./pages/residuos_peligrosos.py')
    mc.protected_content()
    
    # Page header
    st.title("📑 Gestión de Documentos Técnicos")
    st.markdown("---")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["📚 Ver Documentos", "📤 Subir Documento"])
    
    with tab1:
        view_documents_section()
    
    with tab2:
        upload_document_section()

else:
    st.switch_page("./pages/login_home.py")