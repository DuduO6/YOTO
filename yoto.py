import networkx as nx
import pydot
import matplotlib.pyplot as plt
import random

def ler_grafo_dot(path):
    graphs = pydot.graph_from_dot_file(path)
    if not graphs:
        raise ValueError("Nenhum grafo encontrado no arquivo DOT.")
    pydot_graph = graphs[0]

    G = nx.DiGraph()
    for node in pydot_graph.get_nodes():
        name = node.get_name().strip('"')
        if name and name not in ("node", "graph", "edge"):
            G.add_node(name)

    for edge in pydot_graph.get_edges():
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        G.add_edge(src, dst)

    return G

def construir_vizinhanças(G: nx.DiGraph):
    graph_out = {n: list(G.successors(n)) for n in G.nodes()}
    graph_in  = {n: list(G.predecessors(n)) for n in G.nodes()}
    return graph_out, graph_in

def escolher_no_inicial(G: nx.DiGraph, seed=None):
    if seed is not None:
        random.seed(seed)

    fontes = [n for n in G.nodes() if G.in_degree(n) == 0]

    if fontes:  # prioridade: nós sem entradas
        return random.choice(fontes)
    elif len(G) > 0:  # fallback: qualquer nó (preferindo maior fanout)
        candidatos = list(G.nodes())
        max_out = max(G.out_degree(n) for n in candidatos)
        melhores = [n for n in candidatos if G.out_degree(n) == max_out]
        return random.choice(melhores)
    else:
        raise ValueError("Grafo vazio: não há nó inicial.")


def zigzag_yoto(graph_out, graph_in, start, seed=None):
    if seed is not None:
        random.seed(seed)

    visited_nodes = []
    visited_edges = []
    edges_transferidos = []  # arestas com chance de transferir localidade
    edges_perdidos = []      # arestas vistas quando ambos os nós já estavam visitados

    seen_nodes = set()
    seen_edges = set()

    def dfs(node, direction="out"):
        if node not in seen_nodes:
            seen_nodes.add(node)
            visited_nodes.append(node)

        neighbors_out = graph_out.get(node, [])
        neighbors_in  = graph_in.get(node, [])

        # candidatos ainda não percorridos
        candidates_out = [n for n in neighbors_out if (node, n) not in seen_edges]
        candidates_in  = [n for n in neighbors_in  if (n, node) not in seen_edges]

        random.shuffle(candidates_out)
        random.shuffle(candidates_in)

        def follow(u, v, new_dir):
            edge = (u, v)
            if edge in seen_edges:
                return
            seen_edges.add(edge)
            visited_edges.append(edge)

            # se pelo menos um extremo ainda não foi visitado, há transferência de localidade
            if (u not in seen_nodes) or (v not in seen_nodes):
                edges_transferidos.append(edge)
            else:
                edges_perdidos.append(edge)

            dfs(v, new_dir)

        # Explora sucessores (out)
        for nb in candidates_out:
            new_dir = direction
            if len(neighbors_out) >= 2 or len(neighbors_in) >= 2:
                new_dir = "in" if direction == "out" else "out"
            follow(node, nb, new_dir)

        # Explora predecessores (in)
        for nb in candidates_in:
            new_dir = direction
            if len(neighbors_out) >= 2 or len(neighbors_in) >= 2:
                new_dir = "out" if direction == "in" else "in"
            follow(nb, node, new_dir)

    # cobre todos os componentes
    for node in list(graph_out.keys()):
        if node not in seen_nodes:
            dfs(node, "out")

    return visited_nodes, visited_edges, edges_perdidos

def plotar_comparacao_numerada_nos(G, ordem, arestas_zigzag):
    pos = nx.spring_layout(G, seed=42)
    todas_arestas = set(G.edges())
    arestas_percorridas = set(arestas_zigzag)
    arestas_nao_percorridas = list(todas_arestas - arestas_percorridas)

    plt.figure(figsize=(10, 7))

    # Nós não visitados cinza
    nos_nao_visitados = [n for n in G.nodes() if n not in ordem]
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightgray", nodelist=nos_nao_visitados)
    # Nós visitados azul
    nx.draw_networkx_nodes(G, pos, nodelist=ordem, node_color="skyblue", node_size=700)

    # Arestas não percorridas tracejadas
    nx.draw_networkx_edges(
        G, pos, edgelist=arestas_nao_percorridas, style="dashed",
        edge_color="black", arrowsize=15, connectionstyle="arc3,rad=0.1"
    )

    # Arestas percorridas vermelho sólido
    nx.draw_networkx_edges(
        G, pos, edgelist=arestas_zigzag,
        edge_color="red", arrowsize=20, width=2, connectionstyle="arc3,rad=0.1"
    )

    # Numeração dos nós de acordo com a ordem de visita
    node_labels = {node: str(i+1) for i, node in enumerate(ordem)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_weight="bold")

    plt.title("Grafo Original vs Caminho ZigZag do YOTO (nós numerados por ordem de visita)", fontsize=14)
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    arquivo_dot = "exemplo.dot"  # Substitua pelo seu arquivo
    G = ler_grafo_dot(arquivo_dot)

    graph_out, graph_in = construir_vizinhanças(G)
    start = escolher_no_inicial(G)

    ordem, arestas_zigzag, edges_perdidos = zigzag_yoto(graph_out, graph_in, start)

    print("Nó inicial:", start)
    print("\nOrdem de nós visitados (primeira visita):")
    for i, node in enumerate(ordem, 1):
        print(f"{i}: {node}")

    print("\nArestas percorridas (u -> v):")
    for src, dst in arestas_zigzag:
        print(f"{src} -> {dst}")


    if len(edges_perdidos)>0:
        print("\nArestas perdidas (visitadas quando ambos os nós já tinham sido visitados):")
        for src, dst in edges_perdidos:
            print(f"{src} -> {dst}")
    else:
        print("Nenhuma aresta foi perdida")


    plotar_comparacao_numerada_nos(G, ordem, arestas_zigzag)
