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

    for i in shuttles:
        curr_delay.update({i['id']: 0})
        last_query_node.update({i['id']: -1})
        last_stop.update({i['id']: -1})

    while True:
        shuttles = supabase.table("GPS").select("*").execute().data
        G = app.state.G

        for i in shuttles:
            dist=10000
            nearest_node: tuple[int, int] = (-1, -1) 

            for j in app.state.stop_locations[i['assigned_route']]:
                if osmnx.distance.great_circle(j[0], j[1], i['LAT'], i['LONG']) < dist:
                    nearest_node = j
                    dist = osmnx.distance.great_circle(j[0], j[1], i['LAT'], i['LONG'])

            if dist<10:
                if last_query_node[i['id']] == nearest_node:
                    curr_delay[i['id']] += 5
                else:
                    last_query_node[i['id']] = nearest_node
                    curr_delay[i['id']] = 0
            
            if curr_delay[i['id']] >= 20:
                last_stop[i['id']] = nearest_node
                curr_delay[i['id']] = 0

        print(curr_delay)
        print(last_query_node)
        print(last_stop)

        sleep(5)
