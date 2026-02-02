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
from streamlit_js_eval import get_geolocation
import modules.reports as mr
import plotly.express as px

mc.protected_content()

@st.dialog("Firma Aforo")
def firma_dialog(

    vehiculo_placa: str,
    sucursal_id: int,
    evidencia_fachada: BytesIO,
    observaciones: str,
    evidencia_residuos: BytesIO = None,
    optional_photo: BytesIO = None,
    df: pd.DataFrame = None
    
):
    
    lat = None
    lon = None
    # location = get_geolocation()

    # if location and 'error' in location:
    #     if location['error']['code'] == 1:
    #         st.error("Location permission denied")
    #     else:
    #         st.warning(f"Geolocation error: {location['error']['message']}")
    # elif location:
    #     lat = location['coords']['latitude']
    #     lon = location['coords']['longitude']

    nombre = st.text_input("Nombre completo")
    cedula = st.number_input("Cédula", min_value=0, step=1)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        update_streamlit=True,
        height=150,
        width=300,
        key="canvas",
        stroke_width=2
    )

    guardar_aforo(
        df = df,
        vehiculo_placa = vehiculo_placa,
        sucursal_id = sucursal_id,
        evidencia_fachada = evidencia_fachada,
        evidencia_residuos = evidencia_residuos,
        observaciones = observaciones,
        nombre = nombre,
        cedula = cedula,
        canvas_result = canvas_result,
        lat = lat,
        lon = lon,
        optional_photo=optional_photo
        # location = location
    )

def guardar_aforo(
        vehiculo_placa: str,
        sucursal_id: int,
        evidencia_fachada: BytesIO,
        observaciones: str,
        canvas_result,
        lat: float,
        lon: float,
        df: pd.DataFrame = None,
        nombre: str = None,
        cedula: int = None,
        location: dict = None,
        evidencia_residuos: BytesIO = None,
        optional_photo: BytesIO = None
):
    
    if st.button("Confirmar Firma"):
        with st.spinner("Registrando aforo y enviando manifiesto de recolección..."):
            st.toast("⏳ Registrando aforo...")
            # Convert the image data to a PIL Image
            firma = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA') if canvas_result.image_data is not None else None
            buffered = BytesIO()
            firma.save(buffered, format="PNG")

            firma_str = base64.b64encode(buffered.getvalue()).decode() if buffered else None
            evidencia_fachada_str = mc.img_to_b64(evidencia_fachada)
            evidencia_residuos_str = mc.img_to_b64(evidencia_residuos) if evidencia_residuos else None
            optional_photo_str = mc.img_to_b64(optional_photo) if optional_photo else None

            # Create aforo record
            res = mq.create_aforo_record(
                vehiculo_placa=vehiculo_placa,
                operario_name=ss.get('username'),
                sucursal_id=sucursal_id,
                evidencia_fachada=evidencia_fachada_str,
                evidencia_residuos=evidencia_residuos_str,
                nombre_firma=nombre,
                cedula_firma=cedula,
                firma=firma_str,
                observaciones=observaciones,
                latitude=lat,
                longitude=lon
            )

            aforo_id = res.data[0]['id']

            if df is not None:
                df['aforo_id'] = aforo_id
                df.rename(columns={"Item": "residuo"}, inplace=True)
                if 'Peso (kg)' in df.columns:
                    df.rename(columns={"Peso (kg)": "weight"}, inplace=True)
                if 'Tipo de contenedor' in df.columns:
                    df.rename(columns={
                        "Tipo de contenedor": "contenedor",
                        "Cantidad": "cantidad_contenedores"
                        }, inplace=True)
                df = df.to_dict(orient='records')
                mq.create_aforo_residuo_record(df)

            st.toast("⏳ Generando manifiesto de recolección...")

            # fig = px.scatter_map(lat=[lat] if location and 'coords' in location else [],
            #                     lon=[lon] if location and 'coords' in location else [],
            #                     zoom=18, #wont work with values over 18
            #                     color_discrete_sequence=["red"],
            #                     map_style="open-street-map",
            #                     size=[18],
            #                     labels="Ubicación del operario",
            #                     height=800,
            #                     width=600)
            # fig.update_layout(
            #     margin={'t':0,'l':0,'b':0,'r':0}
            # )

            # map_b64 = fig.to_image(format="png")
            # map_b64 = base64.b64encode(map_b64).decode('utf-8')

            aforo = mq.get_aforo_by_id(res.data[0]['id'])
            residues = mq.get_aforos_residues(aforo['id'])


            
            pdf_bytes = mr.generate_aforos_pdf(
                aforo=aforo,
                residues=residues,
                fig_b64=optional_photo_str
                # fig_b64=map_b64
            )

            mc.send_aforo_email(
                to_email=['perez14sebastian@gmail.com'],
                aforo_id=aforo['id'],
                pdf_bytes_io=BytesIO(pdf_bytes)
            )

            st.toast("✅ Manifiesto de recolección enviado por correo.")
            st.rerun()                

            # Send confirmation email with PDF attached         

    # Send confirmation email with PDF attached

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
        is_there_residues = st.radio("¿Hay residuos?", options=['Si', 'No'], index=0, horizontal=True)
        if is_there_residues == 'No':
            st.info("No hay residuos para registrar en este aforo.")
            evidencia_fachada = st.camera_input("Tomar evidencia fotográfica de la fachada")
            firma = st.button("Firmar Aforo")
            if firma:
                if not sucursal_id:
                    st.error("Selecciona primero la sucursal (Ciudad → Cliente → Sucursal)")
                else:
                    firma_dialog(
                        vehiculo_placa=selected_plate,
                        sucursal_id=sucursal_id,
                        evidencia_fachada=evidencia_fachada,
                        observaciones=""
            )
        if is_there_residues == 'Si':
            weight_available = st.radio("¿Hay pesaje disponible?", options=['Si', 'No'], index=0, horizontal=True)
            if weight_available == 'Si':
                peso_df = pd.DataFrame({'Item': ["","","", ""],
                                        'Peso (kg)': [0,0,0,0]})
                displayed_df = st.data_editor(
                    peso_df,
                    num_rows="fixed",
                    hide_index=True,
                    column_config={
                        "Item": st.column_config.SelectboxColumn(
                            "Item",
                            options=mq.get_enum_values('aforo_residue_type'),
                        ),
                        "Peso (kg)": st.column_config.NumberColumn(
                            "Peso (kg)",
                            min_value=0.0,
                            step=0.1,
                        ),
                    },
                )
                total_weight = displayed_df["Peso (kg)"].sum()
            if weight_available == 'No':
            # Allow selecting a container type if weighing isn't available
                volumen_df = pd.DataFrame({'Item': ["","","", ""],
                                        'Tipo de contenedor': ["","","",""],
                                        'Cantidad': [0,0,0,0]})
                displayed_df = st.data_editor(
                    volumen_df,
                    num_rows="fixed",
                    hide_index=True,
                    column_config={
                        "Item": st.column_config.SelectboxColumn(
                            "Item",
                            options=mq.get_enum_values('aforo_residue_type'),
                        ),
                        "Tipo de contenedor": st.column_config.SelectboxColumn(
                            "Tipo de contenedor",
                            options=mq.get_enum_values('aforo_container_type'),
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
                evidencia_residuos = st.camera_input("Tomar evidencia fotográfica de los residuos 1")
            observaciones = st.text_area("Observaciones")
            with columns[0]:
                optional_photo = st.camera_input("Tomar evidencia fotográfica de los residuos 2")

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
                        observaciones=observaciones,
                        optional_photo=optional_photo
                    )

else:
    st.switch_page('./pages/login_home.py')