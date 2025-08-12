import networkx as nx
import pydot

def ler_grafo_dot(path):
    graphs = pydot.graph_from_dot_file(path)
    if not graphs:
        raise ValueError("Nenhum grafo encontrado no arquivo.")
    pydot_graph = graphs[0]

    G = nx.DiGraph()
    for edge in pydot_graph.get_edges():
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        G.add_edge(src, dst)

    return G

def zigzag_traversal_full(graph):
    visited_nodes = []
    visited_nodes_set = set()
    visited_edges = set()

    def dfs(node, going_down=True):
        if node in visited_nodes_set:
            return
        visited_nodes.append(node)
        visited_nodes_set.add(node)

        fanin = graph.in_degree(node)
        fanout = graph.out_degree(node)

        if going_down:
            neighbors = list(graph.successors(node))
        else:
            neighbors = list(graph.predecessors(node))

        neighbors.sort()

        for neighbor in neighbors:
            edge = (node, neighbor) if going_down else (neighbor, node)
            if edge not in visited_edges:
                visited_edges.add(edge)
                dfs(neighbor, going_down)

        # Inverte sentido após visitar vizinhos, se necessário
        if fanin >= 2 or fanout >= 2:
            going_down = not going_down

    for node in graph.nodes():
        if node not in visited_nodes_set:
            dfs(node)

    return visited_edges, visited_nodes


if __name__ == "__main__":
    arquivo_dot = "exemplo.dot"  # Substitua pelo seu arquivo real
    G = ler_grafo_dot(arquivo_dot)

    arestas, ordem = zigzag_traversal_full(G)
    print("Ordem de nós visitados:")
    print(" -> ".join(ordem))

    print("\nArestas percorridas:")
    for src, dst in arestas:
        print(f"{src} -> {dst}")
