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
from modules.nav import MenuButtons

mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:

    mc.logout_and_home()

    MenuButtons(location='home', user_roles=mc.get_roles())

else:
    st.switch_page("./pages/login_home.py") 