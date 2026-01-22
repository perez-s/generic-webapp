import streamlit as st
from streamlit import session_state as ss
import modules.common as mc
import modules.queries as mq
import modules.reports as mr
from io import BytesIO
from streamlit_js_eval import get_geolocation
import base64
import plotly.express as px

mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if not ss.get('authentication_status'):
    st.switch_page('./pages/login_home.py')

mc.logout_and_home('./pages/home.py', layout='centered')

st.title("Reportes — Aforos")
st.write("Genera un PDF con los registros de aforos más recientes.")

location = get_geolocation()

# Check if location permission was denied
if location and 'error' in location:
    if location['error']['code'] == 1:
        st.error("Location permission denied")
    else:
        st.warning(f"Geolocation error: {location['error']['message']}")
elif location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    st.write(f"Latitude: {lat}")
    st.write(f"Longitude: {lon}")

limit = st.number_input("Cantidad de registros", min_value=1, max_value=1000, value=42, step=1)

if st.button("Generar PDF"):
    with st.spinner("Generando PDF..."):
        fig = px.scatter_map(lat=[lat] if location and 'coords' in location else [],
                            lon=[lon] if location and 'coords' in location else [],
                            zoom=18, #wont work with values over 18
                            color_discrete_sequence=["red"],
                            map_style="open-street-map",
                            size=[18],
                            labels="Ubicación del operario",
                            height=800,
                            width=600)
        fig.update_layout(
            margin={'t':0,'l':0,'b':0,'r':0}
        )

        fig_b64 = fig.to_image(format="png")
        fig_b64 = base64.b64encode(fig_b64).decode('utf-8')

        aforos = mq.get_aforo_by_id(limit)
        residues = mq.get_aforos_residues(limit)
        pdf_bytes = mr.generate_aforos_pdf(aforos, residues=residues, fig_b64=fig_b64)
        if pdf_bytes:
            buf = BytesIO(pdf_bytes)
            filename = f"reporte_aforos_{len(aforos)}.pdf"
            st.download_button("Descargar PDF", data=buf.getvalue(), file_name=filename, mime="application/pdf")
            st.success("PDF generado")
        else:
            st.error("No se pudo generar el PDF.")

st.markdown("---")
st.write("Puedes ajustar la cantidad de registros a incluir y volver a generar el PDF.")
