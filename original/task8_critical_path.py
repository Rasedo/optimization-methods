import networkx as nx

tasks = {
    "A": {"duration": 3, "predecessors": []},
    "B": {"duration": 4, "predecessors": []},
    "C": {"duration": 5, "predecessors": ["A"]},
    "D": {"duration": 6, "predecessors": ["A", "B"]},
    "E": {"duration": 2, "predecessors": ["C"]},
    "F": {"duration": 4, "predecessors": ["C", "D"]},
    "G": {"duration": 3, "predecessors": ["E", "F"]},
}

G = nx.DiGraph()
for t, data in tasks.items():
    G.add_node(t, duration=data["duration"])
    for pred in data["predecessors"]:
        G.add_edge(pred, t)

order = list(nx.topological_sort(G))

es = {}
ef = {}
for node in order:
    if not list(G.predecessors(node)):
        es[node] = 0
    else:
        es[node] = max(ef[pred] for pred in G.predecessors(node))
    ef[node] = es[node] + tasks[node]["duration"]

lf = {}
ls = {}
project_duration = max(ef.values())
for node in reversed(order):
    if not list(G.successors(node)):
        lf[node] = project_duration
    else:
        lf[node] = min(ls[succ] for succ in G.successors(node))
    ls[node] = lf[node] - tasks[node]["duration"]

critical = []
for node in order:
    slack = ls[node] - es[node]
    if slack == 0:
        critical.append(node)

print("Длительность проекта:", project_duration)
print("Критический путь:", " -> ".join(critical))
print("ES/EF/LS/LF:")
for node in order:
    print(f"{node}: ES={es[node]}, EF={ef[node]}, LS={ls[node]}, LF={lf[node]}")
