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

mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:
    mc.logout_and_home()
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