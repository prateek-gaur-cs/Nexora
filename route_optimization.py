
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

def show_route_optimization():
    st.title("Route Optimization")
    st.write(
        "Find the lowest-distance route between two locations "
        "using Dijkstra's shortest path algorithm."
    )

    # Sample delivery network: distances are illustrative.
    graph = nx.Graph()

    routes = [
        ("Warehouse", "Hub A", 4),
        ("Warehouse", "Hub B", 7),
        ("Hub A", "Hub B", 2),
        ("Hub A", "City Center", 5),
        ("Hub B", "City Center", 3),
        ("Hub B", "Hub C", 4),
        ("City Center", "Hub C", 2),
        ("Hub C", "Customer Zone", 3),
        ("City Center", "Customer Zone", 8),
    ]

    graph.add_weighted_edges_from(routes)

    locations = sorted(graph.nodes())

    col1, col2 = st.columns(2)

    with col1:
        source = st.selectbox(
            "Starting location",
            locations,
            index=locations.index("Warehouse")
        )

    with col2:
        destination = st.selectbox(
            "Destination",
            locations,
            index=locations.index("Customer Zone")
        )

    if st.button("Find Shortest Route", type="primary"):
        try:
            path = nx.dijkstra_path(
                graph,
                source,
                destination,
                weight="weight"
            )

            distance = nx.dijkstra_path_length(
                graph,
                source,
                destination,
                weight="weight"
            )

            st.success("Shortest route found!")
            st.write("Route:", " → ".join(path))
            st.metric("Total route distance", f"{distance} distance units")

            # Draw the network and highlight the selected route.
            positions = nx.spring_layout(graph, seed=42)

            fig, ax = plt.subplots(figsize=(10, 6))

            nx.draw_networkx(
                graph,
                positions,
                ax=ax,
                node_color="lightblue",
                node_size=2200,
                font_size=8,
                edge_color="gray"
            )

            nx.draw_networkx_edges(
                graph,
                positions,
                edgelist=list(zip(path[:-1], path[1:])),
                edge_color="red",
                width=3,
                ax=ax
            )

            edge_labels = nx.get_edge_attributes(graph, "weight")
            nx.draw_networkx_edge_labels(
                graph,
                positions,
                edge_labels=edge_labels,
                ax=ax
            )

            ax.set_title("Dijkstra Shortest Path")
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig)

            st.caption(
                "Demonstration using a sample network. "
                "Distances are illustrative, not real delivery distances."
            )

        except nx.NetworkXNoPath:
            st.error("No route exists between these locations.")
