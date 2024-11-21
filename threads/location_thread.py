from time import sleep
from exceptiongroup import catch
from fastapi import FastAPI
import requests
from db.supabase import supabase


def test(app: FastAPI):
    shuttles = supabase.table("GPS").select("*").execute().data

    curr_delay = {}
    last_query_node = {}
    last_stop = {}
    reverse_direc = {}

    for i in shuttles:
        curr_delay.update({i["id"]: 0})
        last_query_node.update({i["id"]: (-1, -1)})
        last_stop.update({i["id"]: (-1, -1)})
        reverse_direc.update({i["id"]: False})

    while True:
        shuttles = supabase.table("GPS").select("*").execute().data

        for i in shuttles:
            route: list[tuple] = app.state.stop_locations[i["assigned_route"]]
            dist = 10000
            nearest_node: tuple[int, int] = (-1, -1)

            for stop in route:
                params = {
                    "profile": "car",
                }
                req_string = f"http://graphhopper-container:8989/route?point={i['LAT']},{i['LONG']}&point={stop[0]},{stop[1]}"
                res = requests.get(
                    url=req_string,
                    params=params,
                )
                res = res.json()
                try:
                    if res["paths"][0]["distance"] < dist:
                        nearest_node = stop
                        dist = res["paths"][0]["distance"]
                except:
                    continue

            if dist < 20:
                if last_query_node[i["id"]] == nearest_node:
                    curr_delay[i["id"]] += 5
                else:
                    last_query_node[i["id"]] = nearest_node
                    curr_delay[i["id"]] = 0

            if curr_delay[i["id"]] >= 5:
                if last_stop[i["id"]] != (-1, -1):
                    x = route.index(last_stop[i["id"]])
                    y = route.index(nearest_node)
                    if y == 0:
                        reverse_direc[i["id"]] = False
                    elif y == len(route) - 1:
                        reverse_direc[i["id"]] = True
                    elif x != y:
                        reverse_direc[i["id"]] = y - x < 0

                last_stop[i["id"]] = nearest_node
                curr_delay[i["id"]] = 0

            app.state.reverse_direc = reverse_direc
            app.state.last_stop = last_stop
        print(last_stop, reverse_direc)
        sleep(5)
