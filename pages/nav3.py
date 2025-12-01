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
    st.set_page_config(page_title="Bienvenido a WeroApp", layout="wide")
    mc.logout_and_home()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        residuos_ordinarios = streamlit_tile(
            label="Residuos Ordinarios",
            title="Residuos Ordinarios",
            description="Gestiona la recolección y el reciclaje de residuos ordinarios",
            icon="🗑️",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile"
        )
    with col2:
        residuos_peligrosos = streamlit_tile(
            label="Residuos Peligrosos",
            title="Residuos Peligrosos",
            description="Gestiona la recolección y el reciclaje de residuos peligrosos",
            icon="☣️",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile2"
        )
    with col3:
        madera = streamlit_tile(
            label="Madera",
            title="Madera",
            description="Gestiona la recolección y el reciclaje de residuos de madera",
            icon="🪵",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile3"
        )
    with col1:
        RCD = streamlit_tile(
            label="RCD",
            title="RCD",
            description="Gestiona la recolección y el reciclaje de residuos de construcción y demolición",
            icon="🏗️",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile4"
        )
    if residuos_peligrosos:
        st.info("clicked!")
        st.switch_page("./pages/nav4.py")
else:
    st.switch_page("./pages/login_home.py")