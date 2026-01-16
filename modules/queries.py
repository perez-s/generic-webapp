from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta

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


def list_vehicles():
    try:
        res = supabase.table("vehicles").select("id,plate").order("plate", desc=False).execute()
        return res.data or []
    except Exception as e:
        print(f"Error listing vehicles: {e}")
        return []


def create_aforo(sucursal_id: int, fecha_iso: str, firma: str, observaciones: str, placa_id: int, cantidad: float, item: str, tipo_observacion: str):
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    try:
        payload = {
            "sucursal_id": sucursal_id,
            "fecha": fecha_iso,
            "firma": firma,
            "observaciones": observaciones,
            "placa_id": placa_id,
            "cantidad": cantidad,
            "item": item,
            "tipo_observacion": tipo_observacion,
            "created_at": now,
            "updated_at": now,
        }
        res = supabase.table("aforos").insert(payload).execute()
        return res
    except Exception as e:
        print(f"Error creating aforo: {e}")
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
