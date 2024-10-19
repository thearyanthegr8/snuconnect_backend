import json
from fastapi import APIRouter, Request
import requests
from db.supabase import supabase
import redis

router = APIRouter()


def gphd(lat1, long1, lat2, long2):
    params = {
        "profile": "car",
    }
    req_string = f"http://graphhopper-container:8989/route?point={lat1},{long1}&point={lat2},{long2}"
    res = requests.get(
        url=req_string,
        params=params,
    )
    return res.json()["paths"][0]["distance"]


@router.get("/distance")
async def distance(request: Request, route_id: str):
    redis_resp = request.app.state.r.get(route_id)
    
    if redis_resp:
        print("Cache hit!")
        return json.loads(str(redis_resp))
    
    stop_locations: dict[str, list[tuple]] = request.app.state.stop_locations
    stop_locations_id: dict[str, list[str]] = request.app.state.stop_locations_id
    reverse_direc: dict[str, bool] = request.app.state.reverse_direc
    last_stop = request.app.state.last_stop

    shuttles = (
        supabase.table("GPS").select("*").eq("assigned_route", route_id).execute().data
    )

    n = len(stop_locations[route_id])
    distances: dict[str, list[dict[str, float]]] = {}
    for i in shuttles:
        distances[i["id"]] = []
        try:
            last_stop_index = stop_locations[route_id].index(last_stop[i["id"]])
        except ValueError:
            print("No stop found")
            continue

        if reverse_direc[i["id"]]:
            try:
                distances[i["id"]].append(
                    {
                        stop_locations_id[route_id][last_stop_index - 1]: gphd(
                            i["LAT"],
                            i["LONG"],
                            stop_locations[route_id][last_stop_index - 1][0],
                            stop_locations[route_id][last_stop_index - 1][1],
                        )
                    }
                )
            except:
                print("BUG TRIGGERED!!!")
                distances[i["id"]].append(
                    {stop_locations_id[route_id][last_stop_index]: 0}
                )

            for j in range(last_stop_index - 2, -1, -1):
                distances[i["id"]].append(
                    {
                        stop_locations_id[route_id][j]: gphd(
                            stop_locations[route_id][j + 1][0],
                            stop_locations[route_id][j + 1][1],
                            stop_locations[route_id][j][0],
                            stop_locations[route_id][j][1],
                        )
                        + [*distances[i["id"]][-1].values()][0]
                    }
                )
            for j in range(1, n):
                distances[i["id"]].append(
                    {
                        stop_locations_id[route_id][j]: gphd(
                            stop_locations[route_id][j - 1][0],
                            stop_locations[route_id][j - 1][1],
                            stop_locations[route_id][j][0],
                            stop_locations[route_id][j][1],
                        )
                        + [*distances[i["id"]][-1].values()][0]
                    }
                )
        else:
            try:
                distances[i["id"]].append(
                    {
                        stop_locations_id[route_id][last_stop_index + 1]: gphd(
                            i["LAT"],
                            i["LONG"],
                            stop_locations[route_id][last_stop_index + 1][0],
                            stop_locations[route_id][last_stop_index + 1][1],
                        )
                    }
                )
            except:
                print("BUG TRIGGERED!!!")
                distances[i["id"]].append(
                    {stop_locations_id[route_id][last_stop_index]: 0}
                )

            for j in range(last_stop_index + 2, n):
                distances[i["id"]].append(
                    {
                        stop_locations_id[route_id][j]: gphd(
                            stop_locations[route_id][j - 1][0],
                            stop_locations[route_id][j - 1][1],
                            stop_locations[route_id][j][0],
                            stop_locations[route_id][j][1],
                        )
                        + [*distances[i["id"]][-1].values()][0]
                    }
                )
            for j in range(n - 2, -1, -1):
                distances[i["id"]].append(
                    {
                        stop_locations_id[route_id][j]: gphd(
                            stop_locations[route_id][j + 1][0],
                            stop_locations[route_id][j + 1][1],
                            stop_locations[route_id][j][0],
                            stop_locations[route_id][j][1],
                        )
                        + [*distances[i["id"]][-1].values()][0]
                    }
                )
    request.app.state.r.set(route_id, json.dumps(distances), ex=5)
    return distances
