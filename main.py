from time import sleep
from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections import deque

import osmnx
import osmnx.convert

from threading import Thread

import osmnx.distance
from threads import location_thread

from db.supabase import supabase
from routes.shuttles import router as shuttles_router
from routes.shuttle_id import router as shutttle_id_router
from routes.distance import router as distance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application online!")

    G = osmnx.graph_from_place(
        "Shiv Nadar University, India", custom_filter='["highway"~"service"]'
    )
    G.remove_nodes_from([4227700806, 4227700802, 4314526562, 4227700788, 5287350292])

    app.state.GDF = osmnx.convert.graph_to_gdfs(G)
    app.state.G = G

    all_shuttle_routes: dict[int, list] = {}
    stop_nodes: dict[int, list] = {}

    route_ids = supabase.table("Route").select("*").execute().data
    for i in route_ids:
        shuttle_route = (
            supabase.table("Stops").select("*").eq("route_id", i["id"]).execute().data
        )
        print(shuttle_route)
        all_shuttle_routes.update({i["id"]: shuttle_route})

        temp = []
        for j in shuttle_route:
            temp.append(osmnx.distance.nearest_nodes(G, j["long"], j["lat"]))
        stop_nodes.update({i["id"]: temp})

    app.state.stop_nodes = stop_nodes
    app.state.all_shuttle_routes = all_shuttle_routes

    t = Thread(target=location_thread.test, args=[app], daemon=True).start()

    # osmnx.plot_graph(app.state.G)
    yield
    print("Goodbye!")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": f"{app.state.G.nodes}"}


app.include_router(shuttles_router)
app.include_router(shutttle_id_router)
app.include_router(distance_router)
