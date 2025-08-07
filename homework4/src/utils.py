import networkx as nx


def load_graph(file: str) -> nx.Graph:
    return nx.read_edgelist(
            path=file,
            delimiter=','
        )

def load_weight_graph(file: str) -> nx.Graph:
    return nx.read_weighted_edgelist(
            path=file,
            delimiter=','
    )