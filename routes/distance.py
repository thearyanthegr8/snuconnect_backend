# WORK IN PROGRESS

from fastapi import APIRouter, Request
import networkx as nx
import osmnx
import osmnx.distance
import geopandas
from collections import deque


router = APIRouter()


@router.get("/distance")
async def distance( request: Request):
    G: nx.MultiDiGraph = request.app.state.G
    GDF: geopandas.GeoDataFrame = request.app.state.GDF

    x = GDF.loc[(3729665279, 3973034272, 0), "length"]
    print(x)
    # osmnx.distance.

    return {"distance": 10}
