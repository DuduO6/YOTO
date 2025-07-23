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

def get_fanin(G, node):
    # Retorna a lista dos nós que têm arestas apontando para um nó especifico
    return list(G.predecessors(node))

def get_fanout(G, node):
    #Retorna a lista dos nós em que um nó especifico aponta( sucessor)
    return list(G.successors(node))

def yoto_traversal(G):
    """
    Implementa o algoritmo de travessia ZigZag (YOTO).
    Alterna sentido de visita baseado em fanin/fanout >= 2.
    Percorre todo o grafo, começando por todos os nós de saída e entrada.
    """
    visited = set()
    path = []
    order = []

    # Nós que são saídas (out_degree == 0) e entradas (in_degree == 0)
    start_nodes = set(n for n in G.nodes if G.out_degree(n) == 0 or G.in_degree(n) == 0)
    if not start_nodes:
        start_nodes = set(G.nodes)

    for start in start_nodes:
        if start in visited:
            continue

        # Inicializa direção: se nó é saída (sem sucessores) começa backward, senão forward
        direction = 'backward' if G.out_degree(start) == 0 else 'forward'
        stack = [(start, direction)]

        while stack:
            current, direction = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            order.append(current)

            if direction == 'forward':
                neighbors = get_fanout(G, current)
            else:
                neighbors = get_fanin(G, current)

            for neighbor in neighbors:
                if neighbor not in visited:
                    # Armazena aresta no sentido do percurso
                    if direction == 'forward':
                        path.append((current, neighbor))
                    else:
                        path.append((neighbor, current))

            # Verifica se deve inverter a direção
            fanin = len(get_fanin(G, current))
            fanout = len(get_fanout(G, current))
            if (direction == 'backward' and fanin >= 2) or (direction == 'forward' and fanout >= 2):
                direction = 'forward' if direction == 'backward' else 'backward'

            # Empilha vizinhos não visitados com direção atual
            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append((neighbor, direction))

    # Depois de percorrer os start_nodes, garante que todos os nós foram visitados
    # Percorre os nós restantes não visitados com direção padrão 'forward'
    for node in G.nodes:
        if node not in visited:
            stack = [(node, 'forward')]
            while stack:
                current, direction = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                order.append(current)

                if direction == 'forward':
                    neighbors = get_fanout(G, current)
                else:
                    neighbors = get_fanin(G, current)

                for neighbor in neighbors:
                    if neighbor not in visited:
                        if direction == 'forward':
                            path.append((current, neighbor))
                        else:
                            path.append((neighbor, current))

                fanin = len(get_fanin(G, current))
                fanout = len(get_fanout(G, current))
                if (direction == 'backward' and fanin >= 2) or (direction == 'forward' and fanout >= 2):
                    direction = 'forward' if direction == 'backward' else 'backward'

                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append((neighbor, direction))

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
