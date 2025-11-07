import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64
from pathlib import Path

def protected_content():
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
