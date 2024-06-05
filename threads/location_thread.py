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
            nearest_node = osmnx.distance.nearest_nodes(
                G, i["LONG"], i["LAT"], return_dist=True
            )

            if nearest_node[0] in app.state.stop_nodes[i['assigned_route']] and nearest_node[1]<20:
                if last_query_node[i['id']] == nearest_node[0]:
                    curr_delay[i['id']] += 5
                else:
                    last_query_node[i['id']] = nearest_node[0]
                    curr_delay[i['id']] = 0
            
            if curr_delay[i['id']] >= 20:
                last_stop[i['id']] = nearest_node[0]
                curr_delay[i['id']] = 0

        print(curr_delay)
        print(last_query_node)
        print(last_stop)

        sleep(5)
