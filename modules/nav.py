import streamlit as st
from streamlit import session_state as ss
from streamlit_tile import streamlit_tile
from typing import Literal

hpixels = 200
wpixels = 1000000000

def energia_tile():
    energia = streamlit_tile(
        label="Energía",
        title="Energía",
        description="Controla y optimiza el uso de energía",
        icon="⚡",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="energia_tile"
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
        height=hpixels,
        width=wpixels,
        key="agua_tile"
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
        height=hpixels,
        width=wpixels,
        key="residuos_tile"
    )
    if residuos:
        st.switch_page('pages/residuos_solidos.py')

def residuos_ordinarios_tile():
    residuos_ordinarios = streamlit_tile(
        label="Residuos Ordinarios",
        title="Residuos Ordinarios",
        description="Gestiona la recolección y el reciclaje de residuos ordinarios",
        icon="🗑️",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="residuos_ordinarios_tile"
    )
    if residuos_ordinarios:
        st.toast("Funcionalidad en desarrollo", icon="⚠️")

def residuos_peligrosos_tile():
    residuos_peligrosos = streamlit_tile(
        label="Residuos Peligrosos",
        title="Residuos Peligrosos",
        description="Gestiona la recolección y el reciclaje de residuos peligrosos",
        icon="☣️",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="residuos_peligrosos_tile"
    )
    if residuos_peligrosos:
        st.switch_page("./pages/residuos_peligrosos.py")

def madera_tile():
    madera = streamlit_tile(
        label="Madera",
        title="Madera",
        description="Gestiona la recolección y el reciclaje de residuos de madera",
        icon="🪵",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="madera_tile"
    )
    if madera:
        st.toast("Funcionalidad en desarrollo", icon="⚠️")

def rcds_tile():
    RCDs = streamlit_tile(
        label="RCD",
        title="RCD",
        description="Gestiona la recolección y el reciclaje de residuos de construcción y demolición",
        icon="🏗️",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="rcds_tile"
    )

def providers_tile():
    providers = streamlit_tile(
        label="Proveedores",
        title="Registro de proveedores",
        description="Gestiona la información de los proveedores",
        icon="🏢",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="providers_tile"
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
        height=hpixels,
        width=wpixels,
        key="requests_tile"
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
        height=hpixels,
        width=wpixels,
        key="requests_manage_tile"
    )
    if requests_manage:
        st.switch_page("./pages/request_manage.py")

def mail_test_tile():
    mail_test = streamlit_tile(
        label="Test Email",
        title="Test Email",
        description="Envía un correo electrónico de prueba",
        icon="📧",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="mail_test_tile"
    )
    if mail_test:
        st.switch_page("./pages/mail_test.py")

def render_tiles(tiles_to_render: list):
    counter = 0
    cols = st.columns([1,1,1])
    for i in range(len(tiles_to_render)):
        with cols[counter]:
            tiles_to_render[i]()
            counter += 1
            if counter > 2:
                counter = 0


def MenuButtons(location: Literal['residuos_peligrosos', 'home', 'residuos_solidos'], user_roles=None):

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
        caracol_users = [k for k, v in user_roles.items() if v == 'caracol_users']
        wero = [k for k, v in user_roles.items() if v == 'wero']

        # Show page 1 if the username that logged in is an admin.
        if location == 'home':
            if ss.username in caracol:
                caracol_tiles = [energia_tile, agua_tile, residuos_tile]
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                st.switch_page("./pages/residuos_solidos.py")

            if ss.username in wero:
                wero_tiles = [agua_tile, residuos_tile, energia_tile]
                render_tiles(wero_tiles)
        
        elif location == 'residuos_peligrosos':
            if ss.username in caracol:
                caracol_tiles = [providers_tile, requests_tile, requests_manage_tile]
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                caracol_user_tiles = [requests_tile]
                render_tiles(caracol_user_tiles)

            if ss.username in wero:
                # wero_tiles = [providers_tile, requests_tile, requests_manage_tile, mail_test_tile]
                wero_tiles = [providers_tile, requests_tile, requests_manage_tile]
                render_tiles(wero_tiles)

        elif location == 'residuos_solidos':
            if ss.username in caracol:
                caracol_tiles = [residuos_ordinarios_tile, residuos_peligrosos_tile, madera_tile, rcds_tile]
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                caracol_user_tiles = [residuos_ordinarios_tile, residuos_peligrosos_tile, madera_tile, rcds_tile]
                render_tiles(caracol_user_tiles)

            if ss.username in wero:
                wero_tiles = [residuos_ordinarios_tile, residuos_peligrosos_tile, madera_tile, rcds_tile]
                render_tiles(wero_tiles)
