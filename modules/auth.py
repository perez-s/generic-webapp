from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_user_id(username: str) -> int:
    response = supabase.table('users').select('id').eq('username', username).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]['id']
    else:
        return None
    
def get_provider_id(provider_name: str) -> int:
    response = supabase.table('providers').select('id').eq('provider_name', provider_name).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]['id']
    else:
        return None