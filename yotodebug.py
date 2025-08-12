import networkx as nx
import pydot
import sys
from collections import deque

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
    order = []
    path = []

    # Para evitar registrar arestas duplicadas
    edges_seen = set()

    # Inicializa a fila com nós que têm grau de entrada 0
    start_nodes = [n for n in G.nodes if G.in_degree(n) == 0]
    if not start_nodes:
        start_nodes = list(G.nodes)

    queue = deque()
    for start in start_nodes:
        print(f"[INÍCIO] Inserindo nó inicial na fila: {start} com direção 'forward'")
        queue.append((start, 'forward'))

    # Loop principal para garantir visita de todos os nós
    while queue or len(visited) < len(G.nodes):
        if not queue:
            # Se a fila esvaziar, procura nós não visitados e os adiciona na fila
            unvisited = [n for n in G.nodes if n not in visited]
            if not unvisited:
                break
            print(f"[CONTINUAÇÃO] Fila vazia, adicionando nó não visitado {unvisited[0]} com direção 'forward'")
            queue.append((unvisited[0], 'forward'))

        current, direction = queue.popleft()

        if current in visited:
            print(f"[PULA] Nó {current} já visitado, pulando")
            continue

        print(f"[VISITANDO] Nó: {current} | Direção atual: {direction}")
        visited.add(current)
        order.append(current)

        # Seleciona vizinhos conforme a direção
        neighbors = get_fanout(G, current) if direction == 'forward' else get_fanin(G, current)

        # Avalia possibilidade de inverter direção
        fanout = len(get_fanout(G, current))
        fanin = len(get_fanin(G, current))
        if direction == 'forward' and fanout >= 2:
            next_direction = 'backward'
            print(f"  [INVERSÃO] Direção muda de 'forward' para 'backward' no nó {current} (fanout={fanout})")
        elif direction == 'backward' and fanin >= 2:
            next_direction = 'forward'
            print(f"  [INVERSÃO] Direção muda de 'backward' para 'forward' no nó {current} (fanin={fanin})")
        else:
            next_direction = direction

        for neighbor in neighbors:
            if neighbor not in visited:
                # Registra aresta percorrida e adiciona vizinho na fila
                edge = (current, neighbor) if direction == 'forward' else (neighbor, current)
                if edge not in edges_seen:
                    edges_seen.add(edge)
                    path.append(edge)
                    print(f"  [ARESTA] Percorrendo aresta: {edge[0]} -> {edge[1]}")

                queue.append((neighbor, next_direction))
                print(f"  [FILA] Adicionando nó {neighbor} com direção '{next_direction}' na fila")

    return path, order

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python yoto.py arquivo.dot")
        sys.exit(1)

    arquivo_dot = sys.argv[1]
    G = ler_grafo_dot(arquivo_dot)

    arestas, ordem = yoto_traversal(G)

    print("\nOrdem de nós visitados:")
    print(" -> ".join(ordem))

    print("\nArestas percorridas:")
    for src, dst in arestas:
        print(f"{src} -> {dst}")
