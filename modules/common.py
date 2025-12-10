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
  
def logout_and_home(previous_page: str = None):
    st.set_page_config(page_title="Weroapp", page_icon="./resources/alpha-w-circle-custom.png", layout="wide")
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
    columns = st.columns([1,1,2,1,1,1,2])
    with columns[0]:
        if previous_page:
            st.page_link(previous_page, label="⬅️ Atrás", width="stretch")
        st.page_link("./pages/login_home.py", label="🏠 Inicio", width="stretch")
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

    