import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64
from pathlib import Path
import modules.common as mc
from streamlit_tile import streamlit_tile

authenticator = stauth.Authenticate('config.yaml')
CONFIG_FILENAME = 'config.yaml'
def get_roles():
    """Gets user roles based on config file."""
    with open(CONFIG_FILENAME) as file:
        config = yaml.load(file, Loader=SafeLoader)

    if config is not None:
        cred = config['credentials']
    else:
        cred = {}

    return {username: user_info['role'] for username, user_info in cred['usernames'].items() if 'role' in user_info}
mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:
    columns = st.columns(6)
    with columns[0]:
        st.page_link("./pages/login_home.py", label="🏠 Inicio", use_container_width=True)
        authenticator.logout(button_name='Cerrar sesión', location='main', use_container_width=True, key='logoutformats')
    with columns[5]:
        st.image("./resources/Logo2.png", width=10, use_container_width=True)
    col1, col2, col3 = st.columns([1, 1, 1])

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        providers = streamlit_tile(
            label="Proveedores",
            title="Registro de proveedores",
            description="Gestiona la información de los proveedores",
            icon="🏢",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile"
        )
    with col2:
        requests = streamlit_tile(
            label="Solicitudes",
            title="Solicitudes de recolección",
            description="Gestiona las solicitudes de recolección de materiales",
            icon="📝",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile2"
        )
    with col3:
        requests_manage = streamlit_tile(
            label="Gestión de Solicitudes",
            title="Gestión de Solicitudes",
            description="Gestiona las solicitudes de recolección de materiales",
            icon="🛠️",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile3"
        )
    if providers:
        st.info("🏢 Proveedores clicked!")
        st.switch_page("./pages/providers.py")
    if requests:
        st.info("📝 Solicitudes clicked!")
        st.switch_page("./pages/request.py")
    if requests_manage:
        st.info("🛠️ Gestión de Solicitudes clicke   d!")
        st.switch_page("./pages/request_manage.py")
else:
    st.switch_page("./pages/login_home.py")