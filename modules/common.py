import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta

def protected_content():
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
  
def logout_and_home():
    authenticator = stauth.Authenticate('config.yaml')
    columns = st.columns(6)
    with columns[0]:
        st.page_link("./pages/login_home.py", label="🏠 Inicio", use_container_width=True)
        authenticator.logout(button_name='Cerrar sesión', location='main', use_container_width=True, key='logoutformats')
    with columns[5]:
        st.image("./resources/Logo2.png", width=10, use_container_width=True)
    st.set_page_config(page_title="Bienvenido a WeroApp", layout="wide")
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
