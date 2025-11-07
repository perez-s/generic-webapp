import streamlit as st
from streamlit import session_state as ss
# from modules.nav import MenuButtons
# from pages.Inicio import get_roles, authenticator

# If the user reloads or refreshes the page while still logged in,
# go to the Inicio page to restore the login status. Note reloading
# the page changes the session id and previous state values are lost.
# What we are doing is only to relogin the user.

# Protected content in home page..
def protected_content():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

protected_content()      
if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

elif st.session_state['authentication_status'] is None:
    st.switch_page('pages/login_home.py')

elif ss.get('authentication_status'):
    st.switch_page('pages/login_home.py')

