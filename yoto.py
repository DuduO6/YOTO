import networkx as nx
import pydot
import sys

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

def get_fanout(G, node):
    return list(G.successors(node))

def get_fanin(G, node):
    return list(G.predecessors(node))

def yoto_traversal(G):
    visited = set()
    path = []
    order = []

    def traverse(node, direction):
        visited.add(node)
        order.append(node)

        if direction == 'forward':
            neighbors = get_fanout(G, node)
        else:
            neighbors = get_fanin(G, node)

        fanout = len(get_fanout(G, node))
        fanin = len(get_fanin(G, node))

        if direction == 'forward' and fanout >= 2:
            next_direction = 'backward'
        elif direction == 'backward' and fanin >= 2:
            next_direction = 'forward'
        else:
            next_direction = direction

        for neighbor in neighbors:
            if neighbor not in visited:
                if direction == 'forward':
                    path.append((node, neighbor))
                else:
                    path.append((neighbor, node))
                traverse(neighbor, next_direction)

    # Primeira passada: nós com grau de entrada zero
    start_nodes = [n for n in G.nodes if G.in_degree(n) == 0]
    if not start_nodes:
        start_nodes = list(G.nodes)

    for node in start_nodes:
        if node not in visited:
            traverse(node, 'forward')

    # Segunda passada: cobre componentes desconexos
    for node in G.nodes:
        if node not in visited:
            traverse(node, 'forward')

    return path, order

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python yoto.py arquivo.dot")
        sys.exit(1)

    arquivo_dot = sys.argv[1]
    G = ler_grafo_dot(arquivo_dot)

    arestas, ordem = yoto_traversal(G)

    print("Ordem de nós visitados:")
    print(" -> ".join(ordem))

    print("\nArestas percorridas:")
    for src, dst in arestas:
        print(f"{src} -> {dst}")
