# YOTO Traversal — You Only Traverse Once

O **YOTO (You Only Traverse Once)** é um algoritmo de travessia de grafos direcionados que explora a estrutura do grafo de forma adaptativa. Ele realiza uma varredura inteligente alternando dinamicamente a direção da visita (forward e backward), conforme o grau de entrada e saída dos nós. Essa abordagem é eficiente para percorrer grafos com dependências complexas, como em aplicações de mapeamento de tarefas em arquiteturas CGRA (Coarse-Grained Reconfigurable Architectures).

---

## Funcionamento do Algoritmo

### Leitura do Grafo

O algoritmo começa lendo um grafo no formato `.dot`, utilizando a biblioteca `pydot` para converter o arquivo em um grafo direcionado (`DiGraph`) da biblioteca NetworkX. Todas as arestas definidas no arquivo `.dot` são transformadas em conexões no grafo para análise posterior.

---

### Identificação de Nós Iniciais

Após a leitura, o algoritmo identifica nós com grau de entrada zero (sem predecessores) ou grau de saída zero (sem sucessores). Esses nós são considerados pontos de partida naturais para a travessia. Se nenhum for encontrado, o algoritmo considera todos os nós como candidatos iniciais.

---

### Estratégia de Travessia (Zig-Zag)

A travessia segue um comportamento adaptativo:

- Se a direção inicial for *forward*, a busca segue pelas saídas do nó atual.
- Se for *backward*, a busca segue pelas entradas do nó atual.
- Quando o nó atual possui dois ou mais predecessores (fan-in ≥ 2) ou dois ou mais sucessores (fan-out ≥ 2), a direção da travessia é invertida.
  
Esse comportamento zig-zag evita ciclos desnecessários e garante que todas as partes do grafo sejam alcançadas de maneira eficiente.

---

### Visitação de Nós

O algoritmo mantém uma pilha com tuplas contendo o nó e a direção de visita. A cada iteração, um nó é retirado da pilha:

- Se ainda não tiver sido visitado, ele é marcado como visitado.
- A ordem de visitação é registrada.
- Os vizinhos, dependendo da direção atual, são adicionados à pilha com a direção apropriada.

---

### Arestas Percorridas

Enquanto percorre os nós, o algoritmo também armazena as arestas que foram efetivamente usadas na travessia. Esse conjunto de arestas permite reconstruir o trajeto completo executado pelo algoritmo, útil para visualizações ou para gerar caminhos de execução.

---

### Cobertura Total

Após processar os caminhos que se originam dos nós iniciais, o algoritmo verifica se ainda há nós não visitados. Caso existam, ele reinicia a travessia a partir desses nós, garantindo que o grafo inteiro seja coberto, mesmo em casos com componentes desconexos.

---

### Saída

Ao final da execução, o YOTO exibe:

- A **ordem de nós visitados**, representando a sequência em que os nós foram explorados.
- As **arestas percorridas**, que formam o trajeto real seguido no grafo.

---
