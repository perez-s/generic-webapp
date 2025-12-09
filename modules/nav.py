import streamlit as st
from streamlit import session_state as ss
from streamlit_tile import streamlit_tile
from typing import Literal


def energia_tile():
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
    if energia:
        st.toast("🚧 Funcionalidad en desarrollo...")

def agua_tile():
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
    if agua:
        st.toast("🚧 Funcionalidad en desarrollo...")

def residuos_tile():
    residuos = streamlit_tile(
        label="Residuos solidos",
        title="Residuos solidos",
        description="Gestiona y optimiza la recolección de residuos sólidos",
        icon="🗑️",
        color_theme="blue",
        height="200px",
        width="200px",
        key="demo_tile3"
    )
    if residuos:
        st.switch_page('pages/residuos_solidos.py')

def providers_tile():
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
    if providers:
        st.switch_page("./pages/providers.py")

def requests_tile():
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
    if requests:
        st.switch_page("./pages/request.py")

def requests_manage_tile():
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
    if requests_manage:
        st.switch_page("./pages/request_manage.py")

def render_tiles(tiles_to_render: list):
    counter = 0
    cols = st.columns([1,1,1])
    for tile in tiles_to_render:
        if counter > 2:
            counter = 0
        with cols[counter]:
            tiles_to_render[counter]()
            counter += 1



def MenuButtons(location: Literal['residuos', 'home'], user_roles=None):

    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Always show the home and login navigators.
    #HomeNav()

    # Show the other page navigators depending on the users' role.
    if ss["authentication_status"]:

        # (1) Only the admin role can access page 1 and other pages.
        # In a user roles get all the usernames with admin role.
        caracol = [k for k, v in user_roles.items() if v == 'caracol']
        caracol_users = [k for k, v in user_roles.items() if v == 'usuario_caracol']
        wero = [k for k, v in user_roles.items() if v == 'wero']

        # Show page 1 if the username that logged in is an admin.
        if location == 'home':
            if ss.username in caracol:
                caracol_tiles = [energia_tile, agua_tile, residuos_tile]
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                # caracol_user_tiles = [agua_tile, residuos_tile]
                caracol_user_tiles = [requests_tile]
                render_tiles(caracol_user_tiles)

            if ss.username in wero:
                wero_tiles = [agua_tile, residuos_tile, energia_tile]
                render_tiles(wero_tiles)
        
        elif location == 'residuos':
            if ss.username in caracol:
                caracol_tiles = [providers_tile, requests_manage_tile]
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                caracol_user_tiles = [requests_tile]
                render_tiles(caracol_user_tiles)

            if ss.username in wero:
                wero_tiles = [providers_tile, requests_tile, requests_manage_tile]
                render_tiles(wero_tiles)
        # (2) users with user and admin roles have access to page 2.     
