import streamlit as st
from streamlit import session_state as ss
import modules.common as mc
import modules.queries as mq
from modules.queries import create_client, create_pickup_company, create_vehicle, create_sucursal, get_client_options
from modules.nav import MenuButtons
from datetime import datetime, timezone, timedelta
import time


mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')


# DB interaction functions moved to `modules/queries.py`.


@st.dialog("Crear cliente", width="medium")
def create_client_dialog():
    form = st.form("client_form")
    with form:
        razon_social = st.text_input("Razón social")
        correo = st.text_input("Correo")
        nit = st.text_input("NIT")
        telefono = st.text_input("Teléfono")
        submitted = st.form_submit_button("Crear cliente")
        if submitted:
            if correo and not mc.validate_email(correo):
                return
            if nit:
                try:
                    if not mc.validate_nit(int(nit)):
                        return
                except Exception:
                    st.toast("NIT debe ser numérico", icon="❌")
                    return
            if telefono:
                try:
                    if not mc.validate_phone(int(telefono)):
                        return
                except Exception:
                    st.toast("Teléfono debe ser numérico", icon="❌")
                    return

            result = create_client(razon_social, correo, nit, telefono)
            if result:
                st.toast("✅ Cliente creado exitosamente")
                time.sleep(1)
                st.rerun()

@st.dialog("Crear sucursal", width="medium")
def create_sucursal_dialog():
    form = st.form("sucursal_form")
    with form:
        client_razon_social = st.selectbox("Cliente", options=list(get_client_options().keys()))
        sucursal = st.text_input("Sucursal")
        ciudad = st.text_input("Ciudad")
        direccion = st.text_input("Dirección")
        barrio = st.text_input("Barrio")
        correo = st.text_input("Correo")
        nit = st.text_input("NIT")
        telefono = st.text_input("Teléfono")
        submitted = st.form_submit_button("Crear sucursal")
        if submitted:
            if correo and not mc.validate_email(correo):
                return
            if nit:
                try:
                    if not mc.validate_nit(int(nit)):
                        return
                except Exception:
                    st.toast("NIT debe ser numérico", icon="❌")
                    return
            if telefono:
                try:
                    if not mc.validate_phone(int(telefono)):
                        return
                except Exception:
                    st.toast("Teléfono debe ser numérico", icon="❌")
                    return

            client_options = get_client_options()
            cliente_id = client_options.get(client_razon_social)
            print(cliente_id)
            result = create_sucursal(cliente_id, sucursal, ciudad, direccion, barrio, correo, nit, telefono)
            if result:
                st.toast("✅ Sucursal creada exitosamente")
                time.sleep(1)
                st.rerun()

@st.dialog("Crear empresa de recolección", width="medium")
def create_pickup_company_dialog():
    form = st.form("company_form")
    with form:
        company_name = st.text_input("Nombre de la empresa")
        nit = st.text_input("NIT (opcional)")
        contact = st.text_input("Contacto (opcional)")
        submitted = st.form_submit_button("Crear empresa")
        if submitted:
            if nit:
                try:
                    if not mc.validate_nit(int(nit)):
                        return
                except Exception:
                    st.toast("NIT debe ser numérico", icon="❌")
                    return

            result = create_pickup_company(company_name, nit if nit else None, contact if contact else None)
            if result:
                st.toast("✅ Empresa creada exitosamente")
                time.sleep(1)
                st.rerun()


@st.dialog("Crear vehículo", width="small")
def create_vehicle_dialog():
    form = st.form("vehicle_form")
    with form:
        plate = st.text_input("Placa")
        # Fetch companies for selection
        try:
            companies = mq.supabase.table("pickup_companies").select("id,company_name").order("id", desc=True).execute()
            company_options = {c['company_name']: c['id'] for c in (companies.data or [])}
        except Exception:
            company_options = {}

        if company_options:
            company_name_sel = st.selectbox("Empresa", options=list(company_options.keys()))
            company_id = company_options.get(company_name_sel)
        else:
            st.info("No hay empresas registradas. Crea una primero.")
            company_id = None

        submitted = st.form_submit_button("Crear vehículo")
        if submitted:
            if not plate:
                st.error("La placa es obligatoria")
                return
            if not company_id:
                st.error("Selecciona o crea una empresa antes")
                return

            result = create_vehicle(plate, company_id)
            if result:
                st.toast("✅ Vehículo creado exitosamente")
                time.sleep(1)
                st.rerun()


if ss["authentication_status"]:

    mc.logout_and_home('./pages/residuos_solidos.py')

    st.subheader("📋 Formularios de entrada")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Crear cliente", use_container_width=True):
            create_client_dialog()
    with col2:
        if st.button("➕ Crear empresa de recolección", use_container_width=True):
            create_pickup_company_dialog()
    with col3:
        if st.button("➕ Crear vehículo", use_container_width=True):
            create_vehicle_dialog()
    with col1:
        if st.button("➕ Crear sucursal", use_container_width=True):
            create_sucursal_dialog()

else:
    st.switch_page("./pages/login_home.py")