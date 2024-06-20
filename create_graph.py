import osmnx

G = osmnx.graph_from_place(
        "Shiv Nadar University, India",
        simplify=False,
        custom_filter="['highway'~'service|pedestrian']",
    )
G.remove_nodes_from([4227700806, 4227700802, 4314526562, 4227700788, 5287350292])
osmnx.save_graph_xml(G)
osmnx.plot_graph(G)
    