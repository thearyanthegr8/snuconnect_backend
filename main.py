from fastapi import FastAPI
from contextlib import asynccontextmanager

import osmnx
import networkx as nx
import matplotlib.pyplot as plt
import osmnx.graph
import osmnx.utils_graph

from db.supabase import supabase  # Ensure to import the supabase client
from routes.shuttles import router as shuttles_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.G = osmnx.graph_from_place(
        "Shiv Nadar University, India", custom_filter='["highway"~"service"]'
    )
    app.state.G = app.state.G.to_undirected()
    app.state.G.remove_nodes_from([4227700806, 4227700802, 4314526562, 4227700788])
    # osmnx.plot_graph(app.state.G)
    yield
    print("Goodbye!")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": f"{app.state.G.nodes}"}



app.include_router(shuttles_router)

# @app.get("/shuttles/{shuttle_id}")
# get_shuttle(shuttle_id)
