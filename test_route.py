import networkx as nx

graph = nx.Graph()

graph.add_weighted_edges_from([
    ("Warehouse", "Hub A", 4),
    ("Warehouse", "Hub B", 7),
    ("Hub A", "Hub B", 2),
    ("Hub A", "City Center", 5),
    ("Hub B", "City Center", 3),
    ("Hub B", "Hub C", 4),
    ("City Center", "Hub C", 2),
    ("Hub C", "Customer Zone", 3),
    ("City Center", "Customer Zone", 8),
])

path = nx.dijkstra_path(
    graph,
    "Warehouse",
    "Customer Zone",
    weight="weight"
)

distance = nx.dijkstra_path_length(
    graph,
    "Warehouse",
    "Customer Zone",
    weight="weight"
)

print("Shortest route:", " -> ".join(path))
print("Total distance:", distance)