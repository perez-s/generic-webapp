import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Literal
from streamlit.components.v1 import html
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date

elevencolors = ["blue", "green", "orange", "red", "purple", "brown", "gray", "pink", "teal", "cyan", "magenta"] 
email_password = os.getenv('EMAIL_PASSWORD')  

# def img_to_base64():
#     with open("resources/Logo2.png", "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#     return encoded_string

def utc_to_america_bogota(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to America/Bogota timezone."""
    bogota_tz = timezone(timedelta(hours=-5))
    return utc_dt.astimezone(bogota_tz)

@st.dialog("Actiualizar")
def update_details(authenticator):
    if authenticator.update_user_details(st.session_state.get('username'), fields={
        'Form name':'Actualizar datos de usuario',
        'Field':'Campo',
        'First name':'Nombre',
        'Last name':'Apellido',
        'Email':'Correo electrónico',
        'New value':'Nuevo valor',
        'Update':'Actualizar'}):
                st.success('Entries updated successfully')

def protected_content():
    authenticator = ss.get('authapp')
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
  
def logout_and_home(previous_page: str = None, layout: str = "wide"):
    st.set_page_config(page_title="Weroapp", page_icon="./resources/alpha-w-circle-custom.png", layout=layout)
    st.markdown("""
        <style>
            .block-container {
                    padding-top: 0.2rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
    authenticator = stauth.Authenticate('config.yaml')
    if 'authapp' not in ss:
        ss.authapp = authenticator
    if layout == 'centered':
        st.set_page_config(page_title="Weroapp", page_icon="./resources/alpha-w-circle-custom.png", layout="wide")
        st.markdown("""
            <style>
                .block-container {
                        padding-top: 0rem;
                        padding-bottom: 0rem;
                        padding-left: 1rem;
                        padding-right: 1rem;
                    }
            </style>
            """, unsafe_allow_html=True)
        columns = st.columns([2,1,2])
        with columns[0]:
            st.markdown(f"Sesión iniciada como: **{ss['name']}**")
            authenticator.logout(button_name='Cerrar sesión', location='main', use_container_width=True, key='logoutformats')
        with columns[2]:
            st.image("./resources/Logo2.png", width="stretch")
    if layout == 'wide':
        st.set_page_config(page_title="Weroapp", page_icon="./resources/alpha-w-circle-custom.png", layout=layout)
        st.markdown("""
            <style>
                .block-container {
                        padding-top: 0.2rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """, unsafe_allow_html=True)
        columns = st.columns([1,1,2,1,1,1,2])
        with columns[0]:
            if previous_page:
                st.page_link(previous_page, label="⬅️ Atrás", width="stretch")
            st.page_link("./pages/login_home.py", label="🏠 Inicio", width="stretch")
        with columns[4]:    
            if st.button("🚹 Cuenta", use_container_width=True):
                update_details(authenticator)
            authenticator.logout(button_name='Cerrar sesión', location='main', use_container_width=True, key='logoutformats')
        with columns[2]:
            st.markdown(f"Sesión iniciada como: **{ss['name']}**")
        with columns[6]:
            st.image("./resources/Logo2.png", width="stretch")

    st.divider()

def format_date(date_str: str) -> str:
    # When displaying dates from Supabase, parse and format them
    # Parse ISO format string to datetime
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    # Format as desired
    return date_obj.strftime("%Y %B  %d %H:%M %Z")

def get_roles():
    """Gets user roles based on config file."""
    CONFIG_FILENAME = 'config.yaml'
    with open(CONFIG_FILENAME) as file:
        config = yaml.load(file, Loader=SafeLoader)

    if config is not None:
        cred = config['credentials']
    else:
        cred = {}
    
    return {username: user_info['role'] for username, user_info in cred['usernames'].items() if 'role' in user_info}

def get_email():
    """Gets email based on config file."""
    CONFIG_FILENAME = 'config.yaml'
    with open(CONFIG_FILENAME) as file:
        config = yaml.load(file, Loader=SafeLoader)

    if config is not None:
        cred = config['credentials']
    else:
        cred = {}

    return {username: user_info['email'] for username, user_info in cred['usernames'].items() if 'email' in user_info}

def validate_email(email: str) -> bool:
    """Validates an email address format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return True
    else:
        st.toast("Dirección de correo electrónico inválida.", icon="❌")
        return False

def validate_phone(phone: int) -> bool:
    """Validates a phone number format (simple check)."""
    if len(str(phone)) == 7 or len(str(phone)) == 10:
        return True
    else:
        st.toast("Número de teléfono inválido. Debe tener 7 o 10 dígitos.", icon="❌")
        return False

def validate_nit(nit: int) -> bool:
    """Validates a NIT number format (simple check)."""
    if len(str(nit)) == 9:
        return True
    else:
        st.toast("Número de NIT inválido. Debe tener 9 dígitos.", icon="❌")
        return False

def validate_website(website: str) -> bool:
    """Validates a website URL format."""
    website_regex = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
    if re.match(website_regex, website):
        return True
    else:
        st.toast("URL de sitio web inválida.", icon="❌")
        return False

def validate_residue_types(residues: list) -> bool:
    """Validates that at least one residue type is selected."""
    if not residues or len(residues) == 0:
        st.toast("Debe seleccionar al menos un tipo de residuo.", icon="❌")
        return False
    
    # Define incompatible residue types that must be alone
    must_be_alone = {"Biosanitarios", "Pinturas", "Tóneres"}
    
    # Define oil-related residues that can only be with each other
    oil_related = {"Aceites usados", "Sólidos con aceite"}
    
    # Check if any must-be-alone residue is present
    alone_residues = [r for r in residues if r in must_be_alone]
    if alone_residues:
        if len(residues) > 1:
            st.toast(f"{alone_residues[0]} no puede estar con otro tipo de residuos.", icon="❌")
            return False
        return True
    
    # Check if oil-related residues are mixed with non-oil residues
    has_oil = any(r in oil_related for r in residues)
    has_non_oil = any(r not in oil_related for r in residues)
    
    if has_oil and has_non_oil:
        st.toast("Aceites usados y Sólidos con aceite no pueden estar con otro tipo de residuos.", icon="❌")
        return False
    
    return True

def path_file(provider_nit, file_name, upload_file) -> str:
    try:
        ext = upload_file.type.split('/')[-1]
        return f"uploads/{provider_nit}_{file_name}.{ext}"
    except Exception as e:
        st.toast(f"Error generando ruta de archivo: {e}")

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
        st.toast(f"Error generando rutas de archivos: {e}")
        return []

def save_file(file_uploader, file_path) -> str:
    try:
        with open(file_path, mode='wb') as w:
            w.write(file_uploader.getvalue())
        return file_path
    except Exception as e:
        st.toast(f"Error guardando archivo: {e}")
    
def send_email(to_email: list, operation: Literal['Creation', 'Schedule', 'Cancelled', 'Update'], supabase_return: dict):
    sender_email = 'no-reply@mywero.com.co'
    if operation == 'Creation':
        subject = f'Solicitud No. {supabase_return.get("id")} creada exitosamente'
        created_at = datetime.fromisoformat(supabase_return.get("created_at").replace('Z', '+00:00'))
        created_at = utc_to_america_bogota(created_at)
        txt_content = open('./resources/success_email.txt').read().format(id=supabase_return.get("id"), date=created_at.strftime("%Y-%m-%d %H:%M:%S"), residues=', '.join(supabase_return.get("request_category", [])))
        html_content0 = open('./resources/success_email.html').read()
        html_content = html_content0.replace('{id:}', str(supabase_return.get("id"))).replace('{date:}', created_at.strftime("%Y-%m-%d %H:%M:%S")).replace('{residues:}', ', '.join(supabase_return.get("request_category", [])))
    elif operation == 'Schedule':
        subject = f'Solicitud agendada exitosamente a recolección {supabase_return["id"]}'
        pickup_date = supabase_return['pickup_date']
        request_ids = [request['request_id'] for request in supabase_return['pickup_requests']]
        txt_content = open('./resources/schedule_email.txt').read().format(id=', '.join(map(str, request_ids)), pickup_date=pickup_date)
        html_content0 = open('./resources/schedule_email.html').read().replace('{id:}', ', '.join(map(str, request_ids))).replace('{pickup_date:}', pickup_date)
        html_content = html_content0
    elif operation == 'Update':
        subject = f'Solicitud No. {supabase_return.get("id")} actualizada exitosamente'
        updated_at = datetime.fromisoformat(supabase_return.get("updated_at").replace('Z', '+00:00'))
        updated_at = utc_to_america_bogota(updated_at)
        txt_content = open('./resources/request_update_email.txt').read().format(id=supabase_return.get("id"), date=updated_at.strftime("%Y-%m-%d %H:%M:%S"), residues=', '.join(supabase_return.get("request_category", [])))
        html_content0 = open('./resources/request_update_email.html').read()
        html_content = html_content0.replace('{id:}', str(supabase_return.get("id"))).replace('{date:}', updated_at.strftime("%Y-%m-%d %H:%M:%S")).replace('{residues:}', ', '.join(supabase_return.get("request_category", [])))
    elif operation == 'Cancelled':
        subject = f'Recolección N° {supabase_return["id"]} cancelada'
        request_ids = [request['request_id'] for request in supabase_return['pickup_requests']]
        txt_content = open('./resources/cancel_email.txt').read().format(id=', '.join(map(str, request_ids)), cancel_reason=supabase_return['admin_note'])
        html_content0 = open('./resources/cancel_email.html').read().replace('{id:}', ', '.join(map(str, request_ids))).replace('{cancel_reason:}', supabase_return['admin_note'])
        html_content = html_content0
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ", ".join(to_email)
    msg.attach(MIMEText(txt_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))
    # Send the message via our own SMTP server, but don't include the

    # envelope header.
    try:
        with smtplib.SMTP_SSL('mail.mywero.com.co', 465) as server:
            server.login(sender_email, "QhgD72lIv3pWEher")
            server.send_message(msg)
    except Exception as e:
        st.toast(f"Error enviando correo electrónico: {e}", icon="❌")

def get_email_from_request_id(request_ids: list) -> list:
    """Gets email addresses associated with given request IDs from config.yaml."""
    emails = set()
    email_map = get_email()
    
    for request_id in request_ids:
        for username, email in email_map.items():
            emails.add(email)
    
    return list(emails)