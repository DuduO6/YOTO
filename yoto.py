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

    if fontes:  
        return random.choice(fontes)
    elif len(G) > 0:  
        candidatos = list(G.nodes())
        max_out = max(G.out_degree(n) for n in candidatos)
        melhores = [n for n in candidatos if G.out_degree(n) == max_out]
        return random.choice(melhores)
    else:
        raise ValueError("Grafo vazio: não há nó inicial.")


def zigzag_yoto(graph_out, graph_in, start=None):
    visited_nodes = []
    visited_edges = []
    edges_transferidos = []   
    edges_perdidos = []       

    seen_nodes = set()
    seen_edges = set()        

    def add_edge_and_recurse(u, v, next_node, new_dir):
        e = (u, v)
        if e in seen_edges:
            return
        seen_edges.add(e)

        if next_node not in seen_nodes:
            visited_edges.append(e)
            edges_transferidos.append(e)
        else:
            edges_perdidos.append(e)

        dfs(next_node, new_dir)

    def dfs(node, direction="out"):
        if node not in seen_nodes:
            seen_nodes.add(node)
            visited_nodes.append(node)

        succ = sorted(graph_out.get(node, []))  
        pred = sorted(graph_in.get(node, []))   

        if direction == "out":

            for p in pred:
                if (p, node) not in seen_edges and p not in seen_nodes:
                    add_edge_and_recurse(p, node, p, "in")

            for s in succ:
                if (node, s) not in seen_edges:
                    add_edge_and_recurse(node, s, s, "out")

        else:  # direction == "in"
            for s in succ:
                if (node, s) not in seen_edges and s not in seen_nodes:
                    add_edge_and_recurse(node, s, s, "out")

            for p in pred:
                if (p, node) not in seen_edges:
                    add_edge_and_recurse(p, node, p, "in")

    all_nodes = set(graph_out.keys()) | set(graph_in.keys())
    if start is not None and start in all_nodes and start not in seen_nodes:
        dfs(start, "out")

    for n in sorted(all_nodes):
        if n not in seen_nodes:
            dfs(n, "out")

    return visited_nodes, visited_edges, edges_perdidos, edges_transferidos



def plotar_comparacao_numerada_nos(G, ordem, arestas_zigzag):
    pos = nx.spring_layout(G, seed=42)
    todas_arestas = set(G.edges())
    arestas_percorridas = list(edges_transferidos)
    arestas_nao_percorridas = edges_perdidos

    plt.figure(figsize=(10, 7))

    nos_nao_visitados = [n for n in G.nodes() if n not in ordem]
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightgray", nodelist=nos_nao_visitados)
    nx.draw_networkx_nodes(G, pos, nodelist=ordem, node_color="skyblue", node_size=700)

    nx.draw_networkx_edges(
        G, pos, edgelist=arestas_nao_percorridas, style="dashed",
        edge_color="red", arrowsize=15, connectionstyle="arc3,rad=0.1"
    )

    nx.draw_networkx_edges(
        G, pos, edgelist=arestas_percorridas,
        edge_color="black", arrowsize=20, width=2, connectionstyle="arc3,rad=0.1"
    )

    node_labels = {node: str(i+1) for i, node in enumerate(ordem)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_weight="bold")

    plt.title("Grafo Original vs Caminho ZigZag do YOTO (nós numerados por ordem de visita)", fontsize=14)
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    arquivo_dot = "exemplo2.dot"  
    G = ler_grafo_dot(arquivo_dot)

    graph_out, graph_in = construir_vizinhanças(G)
    start = escolher_no_inicial(G)

    ordem, arestas_zigzag, edges_perdidos, edges_transferidos = zigzag_yoto(graph_out, graph_in, start)

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
