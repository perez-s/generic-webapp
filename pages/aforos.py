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
def firma_dialog():

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        update_streamlit=True,
        height=150,
        key="canvas",
    )
 
    if st.button("Cerrar"):
        st.rerun()
    if st.button("Guardar Aforo"):
        if canvas_result.image_data is not None:
            # Convert the image data to a format suitable for storage (e.g., PNG bytes)

            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Here you would save img_str to your database or wherever needed
            st.toast("✅ Aforo guardado exitosamente")
            st.rerun()
        else:
            st.error("Por favor, realiza una firma antes de guardar.")


if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if ss["authentication_status"]:

    mc.logout_and_home('./pages/home.py', layout='centered')

    st.subheader("📥 Registro de Aforos")

    # Persist Ciudad and Placa between reruns using session_state
    if 'aforos_selected_city' not in ss:
        ss['aforos_selected_city'] = ""
    if 'aforos_sel_plate' not in ss:
        ss['aforos_sel_plate'] = ""

    with st.container(border=True):
        cities = mq.list_cities() or []
        city_options = [""] + cities
        default_city = ss.get('aforos_selected_city', "")
        city_index = city_options.index(default_city) if default_city in city_options else 0
        selected_city = st.selectbox("Ciudad", options=city_options, index=city_index, key='aforos_selected_city')

        vehicles = mq.list_vehicles() or []
        vehicle_map = {v['plate']: v['id'] for v in (vehicles or [])}
        plate_options = [""] + list(vehicle_map.keys())
        default_plate = ss.get('aforos_sel_plate', "")
        plate_index = plate_options.index(default_plate) if default_plate in plate_options else 0
        sel_plate = st.selectbox("Placa", options=plate_options, index=plate_index, key='aforos_sel_plate')
        placa_id = vehicle_map.get(sel_plate) if sel_plate else None



    with st.container(border=True, ):

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
        fecha_date = datetime.now().date()
        fecha_time = datetime.now().time()
        observaciones = st.text_area("Observaciones")
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
                # with columns[0]:
                #     container_options = ["", "Bolsas", "Contenedores", "Tarros", "Sacos", "Palets"]
                #     tipo_contenedor = st.selectbox("Tipo de contenedor", options=container_options, index=0)
                # with columns[1]:
                #     cantidad = st.number_input("Cantidad", format="%f")
            # Allow selecting a container type if weighing isn't available

        firma = st.button("Firmar Aforo")

        if firma:
            firma_dialog()

else:
    st.switch_page('./pages/login_home.py')