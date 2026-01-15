from numpy.random import default_rng as rng
import streamlit as st
from streamlit import session_state as ss
import yaml
import time
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import modules.common as mc

### Page specific imports ###
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import locale
import pandas as pd
from modules.nav import MenuButtons
import matplotlib.pyplot as plt
import plotly.express as px
     
mc.protected_content()
          

authenticator = ss.get('authapp')

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:
    mc.logout_and_home()

    MenuButtons(location='home', user_roles=mc.get_roles())

else:
    st.switch_page("./pages/login_home.py") 