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

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Cargar variables de entorno y configurar Supabase
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


def pending_request_count():
    response = supabase.table('requests').select('*').eq('status', 'Pendiente').execute()
    return len(response.data)

def completed_request_count(category: str = None):
    response = supabase.table('residues_collected').select('*')
    if category is not None:
        response = response.eq('category', category)
    response = response.execute()
    return len(set(item['pickup_id'] for item in response.data if item.get('pickup_id') is not None))

def percentage_completed_requests():
    total_response = supabase.table('requests').select('*').execute()
    completed_response = supabase.table('requests').select('*').eq('status', 'Completada').execute()
    total = len(total_response.data)
    completed = len(completed_response.data)
    if total == 0:
        return 0
    return (completed / total) * 100

def kg_collected_total(category: str = None):
    query = supabase.table('residues_collected').select('real_ammount').eq('measure_type', 'kg')
    if category is not None:
        query = query.eq('category', category)
    response = query.execute()
    total_kg = sum(item['real_ammount'] for item in response.data if item['real_ammount'] is not None)
    return total_kg

def m3_collected_total():
    response = supabase.table('residues_collected').select('real_ammount').eq('measure_type', 'm3').execute()
    total_m3 = sum(item['real_ammount'] for item in response.data if item['real_ammount'] is not None)
    return total_m3

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
            

mc.protected_content()
          

authenticator = ss.get('authapp')

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:
    mc.logout_and_home()

    display_home_dashboard()
    MenuButtons(location='home', user_roles=mc.get_roles())

else:
    st.switch_page("./pages/login_home.py") 