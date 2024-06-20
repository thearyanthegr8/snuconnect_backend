from fastapi import FastAPI
from contextlib import asynccontextmanager

from threading import Thread

import requests

from threads import location_thread

from db.supabase import supabase

from routes.shuttles import router as shuttles_router
from routes.shuttle_id import router as shutttle_id_router
from routes.distance import router as distance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application online!")

    stop_distance: dict[str, list] = {}
    stop_locations: dict[str, list[tuple[float, float]]] = {}

    route_ids = supabase.table("Route").select("*").execute().data
    for i in route_ids:
        shuttle_route = (
            supabase.table("RouteStops")
            .select("*, Stops(*)")
            .eq("route_id", i["id"])
            .order("stop_order")
            .execute()
            .data
        )
        print(shuttle_route)
        route_float = []

        route_float.append(
            (shuttle_route[0]["Stops"]["lat"], shuttle_route[0]["Stops"]["long"])
        )

        stop_locations.update({i["id"]: route_float})

    app.state.stop_locations = stop_locations

    Thread(target=location_thread.test, args=[app], daemon=True).start()
    yield
    print("Goodbye!")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": f"{app.state.G.nodes}"}


app.include_router(shuttles_router)
app.include_router(shutttle_id_router)
app.include_router(distance_router)
