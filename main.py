from fastapi import FastAPI
from contextlib import asynccontextmanager

import osmnx
import networkx as nx
import matplotlib.pyplot as plt
import osmnx.graph
import osmnx.utils_graph


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
