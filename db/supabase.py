from decouple import config
from supabase import create_client, Client

supabase_url = str(config("SUPABASE_URL"))
supabase_key = str(config("SUPABASE_KEY"))

supabase: Client = create_client(supabase_url, supabase_key)