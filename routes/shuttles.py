# FastAPI route to get data of all shuttles on campus

from fastapi import APIRouter
from db.supabase import supabase
from datetime import datetime, timedelta
import pytz

router = APIRouter()


@router.get("/shuttles")
async def get_shuttles():
    shuttles = supabase.table("GPS").select("*").execute()
    ist = pytz.timezone("Asia/Kolkata")

    for i in shuttles.data:
        dt1 = datetime.fromisoformat(i["created_at"])
        dt1_ist = dt1.astimezone(ist)
        dt2_utc = datetime.now(pytz.utc)
        dt2_ist = dt2_utc.astimezone(ist)
        difference = dt2_ist - dt1_ist

        if difference < timedelta(minutes=10):
            i["status"] = "Active"
        else:
            i["status"] = "Inactive"

    return shuttles
