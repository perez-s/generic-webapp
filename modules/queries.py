from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_residuo_corriente_names():
    response = supabase.table("residuo_corriente").select("residuo_name").execute()
    return [item["residuo_name"] for item in response.data]

if __name__ == "__main__":
    print(get_residuo_corriente_names())
