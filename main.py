from array import array
from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections import deque

import osmnx
import osmnx.convert

from db.supabase import supabase
from routes.shuttles import router as shuttles_router
from routes.shuttle_id import router as shutttle_id_router
from routes.distance import router as distance_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application online!")
    app.state.G = osmnx.graph_from_place(
        "Shiv Nadar University, India", custom_filter='["highway"~"service"]'
    )
    app.state.G.remove_nodes_from(
        [4227700806, 4227700802, 4314526562, 4227700788, 5287350292]
    )
    app.state.GDF = osmnx.convert.graph_to_gdfs(app.state.G)[1]

    bus_routes:dict[str, deque] = {}

    route_ids = supabase.table("Route").select("*").execute().data; 
    for i in route_ids:
        bus_route = supabase.table("Stops").select("*").eq("route_id", i['id']).execute().data    
        bus_routes.update({f"{i}":deque(bus_route)})
        
    app.state.bus_routes = bus_routes
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
