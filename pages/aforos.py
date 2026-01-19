import streamlit as st
from streamlit import session_state as ss
import modules.common as mc
import modules.queries as mq
from modules.nav import MenuButtons
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
from io import BytesIO
from PIL import Image
import base64
import pandas as pd

mc.protected_content()

@st.dialog("Firma Aforo")
def firma_dialog(
    df: pd.DataFrame,
    vehiculo_placa: str,
    sucursal_id: int,
    evidencia_fachada: BytesIO,
    evidencia_residuos: BytesIO,
    observaciones: str
):
        nombre = st.text_input("Nombre completo")
        cedula = st.number_input("Cédula", min_value=0, step=1)

        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            update_streamlit=True,
            height=150,
            key="canvas",
        )

        if st.button("Confirmar Firma"):
            operario = ss.get('username')
            # prepare payload fields based on weight vs containers
            ev_fachada_b64 = mc.img_to_b64(evidencia_fachada)
            ev_residuos_b64 = mc.img_to_b64(evidencia_residuos)
            firma_b64 = mc.img_to_b64(canvas_result.image_data)
            
            res = mq.create_aforo_record(
                vehiculo_placa=vehiculo_placa,
                operario_name=operario,
                sucursal_id=sucursal_id,
                evidencia_fachada=ev_fachada_b64,
                evidencia_residuos=ev_residuos_b64,
                nombre_firma=nombre,
                cedula_firma=cedula,
                firma=firma_b64,
                observaciones=observaciones
            )

            # if res and res.status_code == 201:
            if True:
                aforo_id = res.data[0]['id']
                # aforo_id = 1
                # Now insert residues if any
                df['aforo_id'] = aforo_id

                df.rename(columns={
                    "Item": "residuo",
                }, inplace=True)

                if "Peso (kg)" in df.columns:
                    df.rename(columns={
                        "Peso (kg)": "weight"
                    }, inplace=True)
                else:
                    df.rename(columns={
                        "Tipo de contenedor": "contenedor",
                        "Cantidad": "cantidad_contenedor"
                    }, inplace=True)

                residuo_record = df.to_dict(orient='records')
                
                print(residuo_record)
                mq.create_aforo_residuo_record(residuo_record)

                st.toast("✅ Aforo registrado exitosamente")
                st.rerun()

@st.dialog("Ruta del Día")
def todays_route():
    with st.container(border=True):
        cities = mq.list_cities() or []
        city_options = [""] + cities
        default_city = ss.get('aforos_selected_city', "")
        city_index = city_options.index(default_city) if default_city in city_options else 0
        selected_city = st.selectbox("Ciudad", options=city_options, index=city_index, key='aforos_selected_city')

        selected_plate = st.text_input("Placa del vehículo", key='aforos_selected_plate')

        if st.button("Confirmar Ruta"):
            if selected_city and selected_plate:
                mq.create_todays_route(
                    username=ss.get('username'),
                    ciudad_today=selected_city,
                    vehicle_plate=selected_plate
                )
                st.toast("✅ Ruta del día confirmada")
                st.rerun()
            else:
                st.error("Por favor, selecciona ciudad y placa.")

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:

    mc.logout_and_home('./pages/home.py', layout='centered')

    if st.button("Volver al Inicio", type="primary"):
        st.switch_page('./pages/entry_forms.py')

    if st.button("Ruta del Día", type="primary"):
        todays_route()
    st.subheader("📥 Registro de Aforos")

    with st.container(border=True):

        # Attempt to prefill city and plate from today's route for current user
        selected_city = ""
        selected_plate = ""
        if ss.get("username"):
            latest_route = mq.get_latest_todays_route(ss.get("username"))
            if latest_route:
                # set session keys so the top selectors reflect this choice
                selected_city = latest_route.get('ciudad_today') or ""
                selected_plate = latest_route.get('vehicle_plate') or ""
        else:
            selected_city = ""
        # Selection flow: Cliente -> Sucursal (depends on selected_city)
        selected_client_id = None
        client_label = "Cliente"
        if selected_city:
            clients = mq.get_clients_in_city(selected_city)
            client_map = {c['razon_social']: c['id'] for c in (clients or [])}
            if client_map:
                sel_client = st.selectbox(client_label, options=[""] + list(client_map.keys()), index=0)
                if sel_client:
                    selected_client_id = client_map.get(sel_client)
            else:
                st.info("No hay clientes para la ciudad seleccionada.")
        else:
            st.info("Selecciona una ciudad para continuar.")

        sucursal_id = None
        if selected_client_id:
            sucursales = mq.get_sucursales_for_client(selected_client_id, selected_city)
            suc_map = {f"{s.get('sucursal')} ({s.get('direccion','')})": s.get('id') for s in (sucursales or [])}
            if suc_map:
                sel_sucursal = st.selectbox("Sucursal", options=[""] + list(suc_map.keys()), index=0)
                if sel_sucursal:
                    sucursal_id = suc_map.get(sel_sucursal)
            else:
                st.info("No hay sucursales para el cliente seleccionado.")

        # Other inputs
        # Use current date and current time automatically (no user inputs)
        is_there_residues = st.radio("¿Hay residuos?", options=['Si', 'No'], index=1, horizontal=True)
        if is_there_residues == 'No':
            st.info("No hay residuos para registrar en este aforo.")
            st.camera_input("Tomar evidencia fotográfica de la fachada")

        if is_there_residues == 'Si':
            weight_available = st.radio("¿Hay pesaje disponible?", options=['Si', 'No'], index=0, horizontal=True)
            if weight_available == 'Si':
                peso_df = pd.DataFrame(columns=["Item", "Peso (kg)"])
                displayed_df = st.data_editor(
                    peso_df,
                    num_rows="dynamic",
                    column_config={
                        "Item": st.column_config.SelectboxColumn(
                            "Item",
                            options=["cartón", "plástico", "vidrio", "metal", "madera", "electrónicos", "otros"],
                        ),
                        "Peso (kg)": st.column_config.NumberColumn(
                            "Peso (kg)",
                            format="%f",
                        ),
                    },
                )
                total_weight = displayed_df["Peso (kg)"].sum()
                st.markdown(f"**Peso Total:** {total_weight:.2f} kg")
                # with columns[0]:
                #     item = st.selectbox("Item", options=[""] + ["cartón", "plástico", "vidrio", "metal", "madera", "electrónicos", "otros"], index=0)
                # with columns[1]:
                #     peso = st.number_input("Peso (kg)", format="%f")
            if weight_available == 'No':
            # Allow selecting a container type if weighing isn't available
                volumen_df = pd.DataFrame(columns=["Item", "Tipo de contenedor", "Cantidad"])
                displayed_df = st.data_editor(
                    volumen_df,
                    num_rows="dynamic",
                    column_config={
                        "Item": st.column_config.SelectboxColumn(
                            "Item",
                            options=["cartón", "plástico", "vidrio", "metal", "madera", "electrónicos", "otros"],
                        ),
                        "Tipo de contenedor": st.column_config.SelectboxColumn(
                            "Tipo de contenedor",
                            options=["Bolsas", "Contenedores", "Tarros", "Sacos", "Palets"],
                        ),
                        "Cantidad": st.column_config.NumberColumn(
                            "Cantidad",
                            format="%f",
                        ),
                    },
                )
            columns = st.columns(2)
            with columns[0]:
                evidencia_fachada = st.camera_input("Tomar evidencia fotográfica de la fachada")
            with columns[1]:
                evidencia_residuos = st.camera_input("Tomar evidencia fotográfica de los residuos")
            observaciones = st.text_area("Observaciones")
            # derive placa_id from session selected plate

            firma = st.button("Firmar Aforo")

            if firma:
                if not sucursal_id:
                    st.error("Selecciona primero la sucursal (Ciudad → Cliente → Sucursal)")
                else:
                    firma_dialog(
                        df=displayed_df,
                        vehiculo_placa=selected_plate,
                        sucursal_id=sucursal_id,
                        evidencia_fachada=evidencia_fachada,
                        evidencia_residuos=evidencia_residuos,
                        observaciones=observaciones
                    )
                    st.rerun()

else:
    st.switch_page('./pages/login_home.py')