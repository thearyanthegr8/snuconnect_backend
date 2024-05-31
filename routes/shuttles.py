from fastapi import APIRouter
from db.supabase import supabase

router = APIRouter()

@router.get("/shuttles")
async def get_shuttles():
    shuttles = supabase.table("GPS").select("*").execute()
    return shuttles