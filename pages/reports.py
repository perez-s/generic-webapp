import streamlit as st
from streamlit import session_state as ss
import modules.common as mc
import modules.queries as mq
import modules.reports as mr
from io import BytesIO

mc.protected_content()

if 'authentication_status' not in ss:
    st.switch_page('./pages/login_home.py')

if not ss.get('authentication_status'):
    st.switch_page('./pages/login_home.py')

mc.logout_and_home('./pages/home.py', layout='centered')

st.title("Reportes — Aforos")
st.write("Genera un PDF con los registros de aforos más recientes.")

limit = st.number_input("Cantidad de registros", min_value=1, max_value=1000, value=50, step=1)

if st.button("Generar PDF"):
    with st.spinner("Generando PDF..."):
        aforos = mq.get_recent_aforos(limit=int(limit))
        aforo_ids = [a.get('id') for a in aforos if a.get('id')]
        residues_map = mq.get_residues_for_aforos(aforo_ids)
        pdf_bytes = mr.generate_aforos_pdf(aforos, residues_map=residues_map)
        if pdf_bytes:
            buf = BytesIO(pdf_bytes)
            filename = f"reporte_aforos_{len(aforos)}.pdf"
            st.download_button("Descargar PDF", data=buf.getvalue(), file_name=filename, mime="application/pdf")
            st.success("PDF generado")
        else:
            st.error("No se pudo generar el PDF.")

st.markdown("---")
st.write("Puedes ajustar la cantidad de registros a incluir y volver a generar el PDF.")
