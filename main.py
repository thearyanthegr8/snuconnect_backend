from fastapi import FastAPI
from contextlib import asynccontextmanager

import osmnx
import networkx as nx
import matplotlib.pyplot as plt
import osmnx.graph
import osmnx.utils_graph

from decouple import config
from supabase import create_client, Client

supabase_url = config("SUPABASE_URL")
supabase_key = config("SUPABASE_KEY")

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

supabase: Client = create_client(supabase_url, supabase_key)


@app.get("/")
async def root():
    return {"message": f"{app.state.G.nodes}"}

@app.get("/shuttles")
def get_shuttles():
    shuttles = supabase.table("GPS").select("*").execute()
    return shuttles

@app.get("/shuttles/{shuttle_id}")
def get_shuttle(shuttle_id: int):
    return {"message": f"Shuttle {shuttle_id}"}
