# FastAPI route to get data of all shuttles on campus

import json
from fastapi import APIRouter, Request
from db.supabase import supabase
from datetime import datetime, timedelta
import pytz

router = APIRouter()


@router.get("/shuttles")
async def get_shuttles():
    shuttles = supabase.table("GPS").select("id, updated_at, assigned_route").execute()
    ist = pytz.timezone("Asia/Kolkata")

    for i in shuttles.data:
        dt1 = datetime.fromisoformat(i["updated_at"])
        dt1_ist = dt1.astimezone(ist)
        dt2_utc = datetime.now(pytz.utc)
        dt2_ist = dt2_utc.astimezone(ist)
        difference = dt2_ist - dt1_ist

        if difference < timedelta(minutes=10):
            i["status"] = "Active"
        else:
            i["status"] = "Inactive"

    return shuttles.data

@router.get("/routes")
async def get_routes(request: Request):
    return  supabase.table("Route").select("*").execute().data

@router.get("/get-locations")
async def get_locations(request: Request):
    redis_resp = request.app.state.r.get("locations")
    if redis_resp:
        print("Cache hit!")
        return json.loads(str(redis_resp))
    
    data = supabase.table("GPS").select("*").execute().data
    request.app.state.r.set("locations", json.dumps(data), ex=1)
    return data