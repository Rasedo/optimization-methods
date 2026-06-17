import networkx as nx

G = nx.DiGraph()

edges = [(1, 2, 5), (1, 3, 3),
         (2, 4, 2), (2, 5, 6),
         (3, 2, 1), (3, 4, 4), (3, 6, 8),
         (4, 5, 3), (4, 6, 2),
         (5, 6, 1)]

G.add_weighted_edges_from(edges)

path = nx.shortest_path(G, source=1, target=6, weight="weight")
length = nx.shortest_path_length(G, source=1, target=6, weight="weight")

print("Кратчайший путь:", path)
print("Длина пути:", length)
