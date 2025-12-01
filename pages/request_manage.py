import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import locale

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Cargar variables de entorno y configurar Supabase
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Diálogo para responder a una solicitud
@st.dialog("Responder solicitud", width="large")
def answer_request():
    with st.form(f"approval_form_{req['id']}"):
        decision = st.selectbox("Decisión", ["Aprobar", "Rechazar"], key=f"decision_{req['id']}")
        schedule_date = st.date_input("Fecha programada", key=f"schedule_date_{req['id']}")
        admin_note = st.text_area("Nota para el usuario", key=f"admin_note_{req['id']}")
        submitted = st.form_submit_button("Enviar decisión")
        if submitted:
            new_status = "Aprobado" if decision == "Aprobar" else "Rechazado"
            response = request_approval(req['id'], new_status, admin_note)
            if response:
                st.success(f"Solicitud #{req['id']} actualizada a '{new_status}'")

# Interfaz principal de gestión de solicitudes
st.title("🚚 Gestión de solicitudes")

def request_approval(request_id: int, new_status: str, admin_note: str):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        response = supabase.table("requests").update({
            "status": new_status,
            "admin_note": admin_note,
            "updated_at": now
        }).eq("id", request_id).execute()
        return response
    except Exception as e:
        st.error(f"Error updating request: {e}")

st.subheader("✅ Aprobar o rechazar solicitudes")
requests = supabase.table("requests").select(
    "id, username, service_type, estimated_amount, details, status, admin_note, created_at"
).eq("status", "Pendiente").order("id").execute()
for req in requests.data:
    with st.container(border=True):
        created_at = datetime.fromisoformat(req['created_at'].replace('Z', '+00:00')).strftime("%Y %B  %d %H:%M %Z")
        st.markdown(f"**#{req['id']}** — {req['service_type']} • {created_at}")
        st.markdown(f"- **Usuario:** {req['username']}")
        st.markdown(f"- **Peso estimado (kg):** {req['estimated_amount']}")
        st.markdown(f"- **Detalles:** {req['details']}")
        
        if st.button("Responder solicitud", key=f"answer_btn_{req['id']}"):
            answer_request()
    st.divider()