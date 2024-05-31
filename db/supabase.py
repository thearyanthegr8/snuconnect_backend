from decouple import config
from supabase import create_client, Client

supabase_url = config("SUPABASE_URL")
supabase_key = config("SUPABASE_KEY")

supabase: Client = create_client(supabase_url, supabase_key)