from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta
import streamlit as st

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_residuo_corriente_names():
    response = supabase.table("residuo_corriente").select("residuo_name").execute()
    return [item["residuo_name"] for item in response.data]


def create_client(
    razon_social: str,
    correo: str,
    nit: str,
    telefono: str,
):
    try:
        resp = supabase.table("clients").insert({
            "razon_social": razon_social,
            "correo": correo,
            "nit": nit,
            "telefono": telefono,
        }).execute()
        return resp
    except Exception as e:
        print(f"Error creating client: {e}")
        return None

def create_sucursal(
    cliente_id: int,
    sucursal: str,
    ciudad: str,
    direccion: str,
    barrio: str,
    correo: str,
    nit: str,
    telefono: str,
):
    try:
        resp = supabase.table("sucursal").insert({
            "cliente_id": cliente_id,
            "sucursal": sucursal,
            "ciudad": ciudad,
            "direccion": direccion,
            "barrio": barrio,
            "correo": correo,
            "nit": nit,
            "telefono": telefono,
        }).execute()
        return resp
    except Exception as e:
        print(f"Error creating sucursal: {e}")
        return None

def create_pickup_company(company_name: str, nit: str = None, contact: str = None):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        resp = supabase.table("pickup_companies").insert({
            "company_name": company_name,
            "nit": nit,
            "contact": contact,
            "created_at": now,
            "updated_at": now,
        }).execute()
        return resp
    except Exception as e:
        print(f"Error creating pickup company: {e}")
        return None

def create_vehicle(plate: str, company_id: int):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        resp = supabase.table("vehicles").insert({
            "plate": plate,
            "company_id": company_id,
            "created_at": now,
            "updated_at": now,
        }).execute()
        return resp
    except Exception as e:
        print(f"Error creating vehicle: {e}")
        return None


def list_cities():
    try:
        res = supabase.table("sucursal").select("ciudad").execute()
        if not res.data:
            return []
        cities = sorted({r.get("ciudad") for r in res.data if r.get("ciudad")})
        return cities
    except Exception as e:
        print(f"Error listing cities: {e}")
        return []


def get_clients_in_city(city: str):
    try:
        rows = supabase.table("sucursal").select("cliente_id").eq("ciudad", city).execute()
        ids = sorted({r.get("cliente_id") for r in (rows.data or []) if r.get("cliente_id")})
        clients = []
        for cid in ids:
            c = supabase.table("clients").select("id,razon_social").eq("id", cid).execute()
            if c.data:
                clients.append(c.data[0])
        return clients
    except Exception as e:
        print(f"Error fetching clients in city: {e}")
        return []


def get_sucursales_for_client(client_id: int, city: str = None):
    try:
        q = supabase.table("sucursal").select("id,sucursal,ciudad,direccion,barrio").eq("cliente_id", client_id)
        if city:
            q = q.eq("ciudad", city)
        res = q.execute()
        return res.data or []
    except Exception as e:
        print(f"Error fetching sucursales: {e}")
        return []


def create_todays_route(username: str, ciudad_today: str, vehicle_plate: str):
    """Insert a todays_route entry for the given username."""
    try:
        payload = {
            "username": username,
            "ciudad_today": ciudad_today,
            "vehicle_plate": vehicle_plate
        }
        res = supabase.table("todays_route").insert(payload).execute()
        return res
    except Exception as e:
        st.toast(f"Error creating todays_route: {e}")
        return None


def get_latest_todays_route(username: str):
    """Return the latest todays_route row for a username, or None."""
    try:
        tz = timezone(timedelta(hours=-5))
        now = datetime.now(tz)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        res = supabase.table("todays_route").select("*").eq("username", username).gte("created_at", start).lt("created_at", end).order("created_at", desc=True).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error fetching latest todays_route: {e}")
        return None


def create_aforo_record(
        vehiculo_placa: str,
        operario_name: str,
        sucursal_id: int,
        evidencia_fachada: str = None,
        evidencia_residuos: str = None,
        nombre_firma: str = None,
        cedula_firma: str = None,
        firma: dict = None,
        observaciones: str = None,
        latitude: float = None,
        longitude: float = None,
):
    """Insert a record into `aforos` using provided fields. Only non-None values are included."""
    try:
        payload = {
            "vehiculo_placa": vehiculo_placa,
            "operario_name": operario_name,
            "sucursal_id": sucursal_id,
            "evidencia_fachada": evidencia_fachada,
            "evidencia_residuos": evidencia_residuos,
            "nombre_firma": nombre_firma,
            "cedula_firma": cedula_firma,
            "firma": firma,
            "observaciones": observaciones,
            "latitude": latitude,
            "longitude": longitude
        }
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}
        res = supabase.table("aforos").insert(payload).execute()
        return res
    except Exception as e:
        st.toast(f"Error creating aforo record: {e}")
        return None

def create_aforo_residuo_record(residuo_df: dict):
    """Insert a record into `aforos_residues` using provided fields. Only non-None values are included."""
    try:
        res = supabase.table("aforos_residues").insert(residuo_df).execute()
        return res
    except Exception as e:
        print(f"Error creating aforo residuo record: {e}")
        return None

def get_client_options():
    try:
        response = supabase.table("clients").select("id, razon_social").order("id", desc=True).execute()
        return {client['razon_social']: client['id'] for client in (response.data or [])}
    except Exception as e:
        print(f"Error fetching client options: {e}")
        return {}

if __name__ == "__main__":
    print(get_client_options())


def get_recent_aforos(limit: int = 100):
    """Return recent aforos rows (most recent first)."""
    try:
        res = supabase.table("aforos").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except Exception as e:
        print(f"Error fetching recent aforos: {e}")
        return []
    
def get_aforo_by_id(aforo_id: int):
    """Return aforo row by id."""
    try:
        res = supabase.table("aforos").select("*").eq("id", aforo_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error fetching aforo by id: {e}")
        return []

def get_aforos_residues(aforo_id: int):
    """Return aforos_residues rows for given aforo id."""
    try:
        res = supabase.table("aforos_residues").select("*").eq("aforo_id", aforo_id).execute()
        return res.data or []
    except Exception as e:
        print(f"Error fetching residues for aforo id {aforo_id}: {e}")
        return []

def get_residues_for_aforos(aforo_ids: list):
    """Return aforos_residues rows for given aforo ids as a dict keyed by aforo_id."""
    try:
        if not aforo_ids:
            return {}
        # use .in_ to fetch matching aforo_id rows
        res = supabase.table("aforos_residues").select("*").in_("aforo_id", aforo_ids).execute()
        rows = res.data or []
        grouped = {}
        for r in rows:
            key = r.get('aforo_id')
            grouped.setdefault(key, []).append(r)
        return grouped
    except Exception as e:
        print(f"Error fetching residues for aforos: {e}")
        return {}
