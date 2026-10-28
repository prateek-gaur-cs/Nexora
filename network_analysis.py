
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt


def show_network_analysis():
    st.title("Network Connectivity Analysis")
    st.write(
        "Explore connected locations using Breadth-First Search (BFS) "
        "and Depth-First Search (DFS)."
    )

    # Illustrative sample network
    graph = nx.Graph()

    graph.add_edges_from([
        ("Warehouse", "Hub A"),
        ("Warehouse", "Hub B"),
        ("Hub A", "City Center"),
        ("Hub B", "City Center"),
        ("Hub B", "Hub C"),
        ("City Center", "Customer Zone"),
        ("Hub C", "Customer Zone"),
        ("Isolated Hub", "Remote Zone"),
    ])

    locations = sorted(graph.nodes())

    start = st.selectbox(
        "Select starting location",
        locations,
        key="network_start"
    )

    algorithm = st.radio(
        "Choose graph algorithm",
        ["BFS", "DFS"],
        horizontal=True
    )

    if st.button("Analyze Network", type="primary"):
        if algorithm == "BFS":
            traversal = list(nx.bfs_tree(graph, start).nodes())
        else:
            traversal = list(nx.dfs_preorder_nodes(graph, start))

        st.subheader(f"{algorithm} Traversal Order")
        st.write(" → ".join(traversal))

        reachable = set(traversal)
        unreachable = sorted(set(graph.nodes()) - reachable)

        st.metric("Reachable locations", len(reachable))

        if unreachable:
            st.warning(
                "Locations not reachable from the selected start: "
                + ", ".join(unreachable)
            )
        else:
            st.success("All locations are reachable from this start.")

        positions = nx.spring_layout(graph, seed=42)
        fig, ax = plt.subplots(figsize=(9, 5))

        node_colors = [
            "lightgreen" if node in reachable else "lightcoral"
            for node in graph.nodes()
        ]

        nx.draw_networkx(
            graph,
            positions,
            node_color=node_colors,
            node_size=1800,
            font_size=8,
            ax=ax
        )

        ax.set_title(f"{algorithm} Network Traversal")
        ax.axis("off")

        st.pyplot(fig)
        plt.close(fig)

        st.caption(
            "Sample network for demonstration; locations are illustrative."
        )
