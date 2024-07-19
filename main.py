from fastapi import FastAPI
from contextlib import asynccontextmanager

from threading import Thread

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
    stop_locations_id: dict[str, list[str]] = {}

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

        route_float = []
        stop_id = []
        for j in shuttle_route:
            route_float.append((j["Stops"]["lat"], j["Stops"]["long"]))
            stop_id.append(j["Stops"]["id"])

        stop_locations.update({i["id"]: route_float})
        stop_locations_id.update({i["id"]: stop_id})

    app.state.stop_locations = stop_locations
    app.state.stop_locations_id = stop_locations_id
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
