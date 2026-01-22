import streamlit as st
from streamlit import session_state as ss
from streamlit_tile import streamlit_tile
from typing import Literal
import os
from supabase import create_client, Client
from dotenv import load_dotenv

hpixels = 200
wpixels = 1000000000

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def completed_request_count(category: str = None):
    response = supabase.table('residues_collected').select('*')
    if category is not None:
        response = response.eq('category', category)
    response = response.execute()
    return len(set(item['pickup_id'] for item in response.data if item.get('pickup_id') is not None))

def kg_collected_total(category: str = None):
    query = supabase.table('residues_collected').select('real_ammount').eq('measure_type', 'kg')
    if category is not None:
        query = query.eq('category', category)
    response = query.execute()
    total_kg = sum(item['real_ammount'] for item in response.data if item['real_ammount'] is not None)
    return total_kg

def display_metric(col,title,data,color="normal",delta=None,border=True):
    with col:
        st.metric(title, data, border=border, delta_color=color, delta=delta, delta_arrow="off")

def display_home_dashboard():
    with st.container(border=True):
        st.subheader("🗑️ Residuos Sólidos")
        cols = st.columns(2)
        display_metric(cols[0], "**✅ Recolecciones gestionadas**", completed_request_count())
        display_metric(cols[1], "**⚖️ Kg gestionados**", f"{kg_collected_total():,.0f} kg")
        with cols[0]:
            cols1 = st.columns(4)
            display_metric(cols1[0], "**🏗️ RCD**", completed_request_count('RCD'), delta=" ", color="normal")
            display_metric(cols1[1], "**🗑️ Ordinarios**", completed_request_count('Ordinarios'), delta=" ", color="normal")
            display_metric(cols1[2], "**🪵 Madera**", completed_request_count('Madera'), delta=" ", color="normal")
            display_metric(cols1[3], "**☣️ RESPEL**", completed_request_count('RESPEL'), delta=" ", color="normal")
        with cols[1]:
            cols1 = st.columns(4)
            total_kg = kg_collected_total()
            if total_kg > 0:
                display_metric(cols1[0], "**🏗️ RCD**", f"{kg_collected_total('RCD')*100/total_kg:0.0f} %", delta=f"{kg_collected_total('RCD')} kg",color="normal")
                display_metric(cols1[1], "**🗑️ Ordinarios**", f"{kg_collected_total('Ordinarios')*100/total_kg:0.0f} %", delta=f"{kg_collected_total('Ordinarios')} kg",color="normal")
                display_metric(cols1[2], "**🪵 Madera**", f"{kg_collected_total('Madera')*100/total_kg:0.0f} %", delta=f"{kg_collected_total('Madera')} kg",color="normal")
                display_metric(cols1[3], "**☣️ RESPEL**", f"{kg_collected_total('RESPEL')*100/total_kg:0.0f} %", delta=f"{kg_collected_total('RESPEL')} kg",color="normal")
            else:
                display_metric(cols1[0], "**🏗️ RCD**", "0 %", delta="0 kg",color="normal")
                display_metric(cols1[1], "**🗑️ Ordinarios**", "0 %", delta="0 kg",color="normal")
                display_metric(cols1[2], "**🪵 Madera**", "0 %", delta="0 kg",color="normal")
                display_metric(cols1[3], "**☣️ RESPEL**", "0 %", delta="0 kg",color="normal")
       
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

def technical_docs_tile():
    technical_docs = streamlit_tile(
        label="Documentos Técnicos",
        title="Documentos Técnicos",
        description="Gestiona la documentación técnica del sistema",
        icon="📑",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="technical_docs_tile"
    )
    if technical_docs:
        st.switch_page("./pages/technical_docs.py")

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

def aforos_tile():
    aforos = streamlit_tile(
        label="Aforos",
        title="Aforos",
        description="Monitorea y gestiona los aforos",
        icon="📊",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="aforos_tile"
    )
    if aforos:
        st.switch_page("./pages/aforos.py")

def entry_forms_tile():
    entry_forms = streamlit_tile(
        label="Formularios de entrada",
        title="Formularios de entrada",
        description="Gestiona los formularios de entrada de datos",
        icon="📝",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="entry_forms_tile"
    )
    if entry_forms:
        st.switch_page("./pages/entry_forms.py")

def reports_tile():
    reports = streamlit_tile(
        label="Reportes",
        title="Reportes",
        description="Genera y descarga reportes en PDF",
        icon="📄",
        color_theme="blue",
        height=hpixels,
        width=wpixels,
        key="reports_tile"
    )
    if reports:
        st.switch_page("./pages/reports.py")

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
        testing = [k for k, v in user_roles.items() if v == 'testing']


        # Show page 1 if the username that logged in is an admin.
        if location == 'home':
            if ss.username in caracol:
                caracol_tiles = [energia_tile, agua_tile, residuos_tile]
                display_home_dashboard()
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                st.switch_page("./pages/residuos_solidos.py")

            if ss.username in wero:
                wero_tiles = [agua_tile, residuos_tile, energia_tile]
                display_home_dashboard()
                render_tiles(wero_tiles)

            if ss.username in testing:
                st.switch_page("./pages/aforos.py")
                # testing_tiles = [aforos_tile, entry_forms_tile, reports_tile]
                # render_tiles(testing_tiles)
        
        elif location == 'residuos_peligrosos':
            if ss.username in caracol:
                caracol_tiles = [providers_tile, requests_tile, requests_manage_tile, technical_docs_tile]
                render_tiles(caracol_tiles)

            if ss.username in caracol_users:
                caracol_user_tiles = [requests_tile, technical_docs_tile]
                render_tiles(caracol_user_tiles)

            if ss.username in wero:
                # wero_tiles = [providers_tile, requests_tile, requests_manage_tile, mail_test_tile]
                wero_tiles = [providers_tile, requests_tile, requests_manage_tile, technical_docs_tile]
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
