import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64
from pathlib import Path
from modules.common import protected_content
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
protected_content()
def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.

    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #00A887;
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def hide_header():
    st.markdown(
        """
            <style>
                    .stAppHeader {
                        background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
                        visibility: visible;  /* Ensure the header is visible */
                    }

                .block-container {
                        padding-top: 1rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """,
        unsafe_allow_html=True,
    )
 
def white_form():
    css="""
        <style>
            [data-testid="stForm"] {
                background: #ffffff;

            }
        </style>
    """
    st.write(css, unsafe_allow_html=True)

def purple_form():
    css="""
        <style>
            [data-testid="stForm"] {
                background: #f0e6ff;

            }
        </style>
    """
    st.write(css, unsafe_allow_html=True)   

def logout():
    columns = st.columns(6)
    with columns[0]:
        authenticator.logout(button_name='Cerrar sesión', location='main', use_container_width=True, key='logoutformats')
    with columns[5]:
        st.image("./resources/Logo2.png", width=10, use_container_width=True)
    st.set_page_config(page_title="Bienvenido a WeroApp", layout="wide")

st.set_page_config(page_title="Bienvenido a WeroApp", layout="centered")

if 'authapp' not in ss:
    ss.authapp = authenticator

authenticator.login(location='main', fields={'Form name':'Iniciar sesión', 'Username':'Usuario', 'Password':'Contraseña', 'Login':'Ingresar', 'Captcha':'Captcha'}, key='loginhome1')


if ss["authentication_status"]:
    logout()
    st.set_page_config(page_title="Bienvenido a WeroApp", layout="wide")

    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        agua = streamlit_tile(
            label="Agua",
            title="Agua",
            description="Monitorea y gestiona el consumo de agua",
            icon="💧",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile"
        )
    with col2:
        energia = streamlit_tile(
            label="Energía",
            title="Energía",
            description="Controla y optimiza el uso de energía",
            icon="⚡",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile2"
        )
    with col3:
        residuos = streamlit_tile(
            label="Residuos solidos",
            title="Residuos solidos",
            description="Gestiona la recolección y el reciclaje de residuos sólidos",
            icon="🗑️",
            color_theme="blue",
            height="200px",
            width="200px",
            key="demo_tile3"
        )
    if residuos:
        st.info("🗑️ Residuos clicked!")
        st.switch_page('pages/nav3.py')
    st.space("large")
if ss["authentication_status"] is False:
    st.toast('Usuario/contraseña incorrecta', icon="🚫")
    set_bg_hack('./resources/homepage1.jpg')
    hide_header()
    white_form()
elif ss["authentication_status"] is None:
    st.toast('Por favor ingresa usuario y contraseña', icon="⚠️")
    set_bg_hack('./resources/homepage1.jpg')
    hide_header()
    white_form()
