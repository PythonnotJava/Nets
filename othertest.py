# Define a function to perform automatic layout and visualization for an undirected graph
import matplotlib.pyplot as plt
import networkx as nx


# Sample function to plot a graph with automatic layout using Fruchterman-Reingold layout
def plot_graph_with_auto_layout(edges):
    """
    Plot an undirected graph with automatic layout to avoid crossing edges and enhance layout regularity.

    Parameters:
    - edges: list of tuples, where each tuple contains (node1, node2, weight)

    Example:
    edges = [
        ('A', 'B', 1), ('A', 'C', 2), ('A', 'E', 4),
        ('B', 'C', 2), ('B', 'E', 2),
        ('C', 'E', 4),
        ('E', 'F', 1)
    ]
    """
    # Create an undirected graph
    G = nx.Graph()

    # Add edges and weights to the graph
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=edge[2])

    # Use the Fruchterman-Reingold force-directed algorithm for layout
    pos = nx.spring_layout(G, weight='weight', seed=42)  # `weight` influences edge lengths

    # Draw the nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')

    # Draw the edges with thickness proportional to the weight
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=edge_weights)

    # Draw the labels for nodes and edges
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): w for u, v, w in edges}, font_size=8)

    # Display the graph
    plt.axis('off')
    plt.show()


# Sample edge list for testing
sample_edges = [
    ('A', 'B', 1), ('A', 'C', 2), ('A', 'E', 4),
    ('B', 'C', 2), ('B', 'E', 2),
    ('C', 'E', 4),
    ('E', 'F', 1)
]

# Run the function with sample edges to visualize the graph with automatic layout
plot_graph_with_auto_layout(sample_edges)
