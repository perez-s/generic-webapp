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
    columns = st.columns([1,1,2,1,1,1,2])
    with columns[0]:
        st.page_link("./pages/residuos_peligrosos.py", label="⬅️ Atrás", width="stretch")
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