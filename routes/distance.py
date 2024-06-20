# WORK IN PROGRESS

from platform import node
from fastapi import APIRouter, Request
import requests
from db.supabase import supabase

router = APIRouter()


@router.get("/distance")
async def distance(request: Request, route_id: str):
    stop_locations: dict[str, list[tuple]] = request.app.state.stop_locations
    reverse_direc: dict[str, bool] = request.app.state.reverse_direc
    last_stop = request.app.state.last_stop

    shuttles = (
        supabase.table("GPS").select("*").eq("assigned_route", route_id).execute().data
    )
    n = len(stop_locations[route_id])
    distances = [0 for i in range(n)]
    for i in shuttles:
        try:
            last_stop_index = stop_locations[route_id].index(last_stop[i["id"]])

            params = {
                "profile": "car",
            }

            req_string = f"http://127.0.0.1:8989/route?point={i['LAT']},{i['LONG']}&point={stop_locations[route_id][last_stop_index+1][0]},{stop_locations[route_id][last_stop_index+1][1]}"
            res = requests.get(
                url=req_string,
                params=params,
            )
            # if reverse_direc[i]:

            # else:

        except ValueError:
            print("No stop found")

    return distances
