from decouple import config
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

supabase_url = str(os.environ.get("SUPABASE_URL"))
supabase_key = str(os.environ.get("SUPABASE_KEY"))

supabase: Client = create_client(supabase_url, supabase_key)