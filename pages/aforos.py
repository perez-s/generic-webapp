import streamlit as st
import modules.common as mc
from streamlit import session_state as ss
from modules.nav import MenuButtons

mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:

    mc.logout_and_home('./pages/residuos_solidos.py')

else:
    st.switch_page("./pages/login_home.py")