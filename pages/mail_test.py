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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Cargar variables de entorno y configurar Supabase
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

### Functions for the page ###

def send_test_email():
    try:
        # Create the email content
        sender_email = 'perez14sebastian@gmail.com'
        email_password = 'jfxh swec svci dili'  
        body = 'This is the body of the email.'

        # me == the sender's email address
        # you == the recipient's email address
        msg = MIMEMultipart()
        msg['Subject'] = 'The contents of the email'
        msg['From'] = sender_email
        msg['To'] = 'perez14sebastian@gmail.com'
        msg.attach(MIMEText(body, 'plain'))
        # Send the message via our own SMTP server, but don't include the

        # envelope header.
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(msg)
        st.success('Test email sent!')
    except Exception as e:
        st.toast(f"Error sending email: {e}", icon="⚠️")

if st.button('Send test email'):
    send_test_email()