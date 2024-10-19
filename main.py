from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from threading import Thread

import redis

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

    app.state.r = redis.Redis(host='redis', port=6379, decode_responses=True, charset='utf-8')
    app.state.stop_locations = stop_locations
    app.state.stop_locations_id = stop_locations_id
    Thread(target=location_thread.test, args=[app], daemon=True).start()
    yield
    print("Goodbye!")


app = FastAPI(lifespan=lifespan)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello world"}


app.include_router(shuttles_router)
app.include_router(shutttle_id_router)
app.include_router(distance_router)
