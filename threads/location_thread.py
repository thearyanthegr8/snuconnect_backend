from time import sleep
from fastapi import FastAPI
import osmnx.distance
from db.supabase import supabase
import osmnx


def test(app: FastAPI):
    shuttles = supabase.table("GPS").select("*").execute().data

    curr_delay = {}
    last_query_node = {}
    last_stop = {}
    reverse_direc = False

    for i in shuttles:
        curr_delay.update({i["id"]: 0})
        last_query_node.update({i["id"]: (-1, -1)})
        last_stop.update({i["id"]: (-1, -1)})

    while True:
        shuttles = supabase.table("GPS").select("*").execute().data

        for i in shuttles:
            route: list[tuple[int, int]] = app.state.stop_locations[i["assigned_route"]]
            dist = 10000
            nearest_node: tuple[int, int] = (-1, -1)

            for stop in route:
                if (
                    osmnx.distance.great_circle(stop[0], stop[1], i["LAT"], i["LONG"])
                    < dist
                ):
                    nearest_node = stop
                    dist = osmnx.distance.great_circle(
                        stop[0], stop[1], i["LAT"], i["LONG"]
                    )

            if dist < 10:
                if last_query_node[i["id"]] == nearest_node:
                    curr_delay[i["id"]] += 5
                else:
                    last_query_node[i["id"]] = nearest_node
                    curr_delay[i["id"]] = 0

            if curr_delay[i["id"]] >= 15:
                if last_stop[i["id"]] != (-1, -1):
                    x = route.index(last_stop[i["id"]])
                    y = route.index(nearest_node)
                    reverse_direc = y - x < 0

                last_stop[i["id"]] = nearest_node
                curr_delay[i["id"]] = 0

            app.state.reverse_direc = reverse_direc
            app.state.last_stop = last_stop

        print(curr_delay)
        print(last_query_node)
        print(last_stop)

        sleep(5)
