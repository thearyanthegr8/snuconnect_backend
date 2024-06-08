from itertools import accumulate
from time import sleep
from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections import deque

import osmnx
import osmnx.convert
import osmnx.distance
import osmnx.routing
from geopandas import GeoDataFrame

from threading import Thread

from threads import location_thread

from db.supabase import supabase

from routes.shuttles import router as shuttles_router
from routes.shuttle_id import router as shutttle_id_router
from routes.distance import router as distance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Application online!')

    G = osmnx.graph_from_place(
        'Shiv Nadar University, India', custom_filter="['highway'~'service|pedestrian']"
    )
    G.remove_nodes_from([4227700806, 4227700802, 4314526562, 4227700788, 5287350292])

    app.state.G = G
    GDF = osmnx.convert.graph_to_gdfs(G)
    
    stop_distance: dict[int, list] = {}
    stop_locations: dict[int, list[tuple[float, float]]] = {}

    route_ids = supabase.table('Route').select('*').execute().data
    for i in route_ids:
        shuttle_route = (
            supabase.table('Stops').select('*').eq('route_id', i['id']).execute().data
        )
        dist = []
        temp = []
        for j in shuttle_route:
            temp.append((j['lat'], j['long']))
        
        for j in range(1, len(temp)):
            start = temp[j-1]
            end = temp[j]
            start_node = osmnx.distance.nearest_nodes(G, start[1], start[0])
            end_node = osmnx.distance.nearest_nodes(G, end[1], end[0])
            path = osmnx.routing.shortest_path(G, start_node, end_node)

            total_distance = 0
            if path and len(path)>1:
                temp_gfd: GeoDataFrame = osmnx.routing.route_to_gdf(G, path)
                route_length: list = list(accumulate(temp_gfd['length']))
                total_distance += route_length[-1]

            start_node_loc = GDF[0].loc[start_node]
            end_node_loc =  GDF[0].loc[end_node]

            total_distance += osmnx.distance.great_circle(start[0], start[1], start_node_loc.y, start_node_loc.x)
            total_distance += osmnx.distance.great_circle(end[0], end[1], end_node_loc.y, end_node_loc.x)
            
            dist.append(total_distance)

        stop_distance.update({i['id']: dist})
        stop_locations.update({i['id']: temp})


    app.state.stop_distance = stop_distance
    app.state.stop_locations = stop_locations

    Thread(target=location_thread.test, args=[app], daemon=True).start()

    # osmnx.plot_graph(app.state.G)
    yield
    print('Goodbye!')


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return {'message': f'{app.state.G.nodes}'}


app.include_router(shuttles_router)
app.include_router(shutttle_id_router)
app.include_router(distance_router)
