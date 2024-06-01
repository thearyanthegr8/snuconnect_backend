# FastAPI route to get data of a specific shuttle by its ID

from fastapi import APIRouter
from db.supabase import supabase
from datetime import datetime, timedelta
import pytz

router = APIRouter()


@router.get("/shuttle/{shuttle_id}")
async def get_shuttle(shuttle_id: int):
    shuttles = supabase.table("GPS").select("*").eq("id", shuttle_id).execute()
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
