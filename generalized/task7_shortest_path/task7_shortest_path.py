import argparse
import json
import os
import sys
import networkx as nx

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_PATH = os.path.join(SCRIPT_DIR, "data", "default.json")


def read_json(path):
    with open(path, "r", encoding="utf-8") as data_file:
        return json.load(data_file)


def load_data(args):
    if args.input:
        return read_json(args.input)
    if args.interactive:
        return prompt_data()
    return read_json(DEFAULT_DATA_PATH)


def prompt_data():
    print("Ввод данных задачи о кратчайшем пути.")
    directed_answer = input("Граф ориентированный? (y/n, Enter = y): ").strip().lower()
    directed = directed_answer in ("", "y", "yes", "да", "д")
    number_of_edges = int(input("Число рёбер: ").strip())

    edges = []
    for edge_number in range(number_of_edges):
        raw = input(f"Ребро {edge_number + 1} (формат: откуда куда вес): ").strip().split()
        start_vertex, end_vertex, weight = raw[0], raw[1], float(raw[2])
        edges.append([start_vertex, end_vertex, weight])

    source = input("Начальная вершина: ").strip()
    target = input("Конечная вершина: ").strip()

    return {
        "directed": directed,
        "source": source,
        "target": target,
        "edges": edges
    }


def validate(data):
    for index, edge in enumerate(data["edges"]):
        if len(edge) != 3:
            raise ValueError(f"Ребро 'edges'[{index}] должно иметь формат [откуда, куда, вес].")
        if edge[2] < 0:
            raise ValueError(f"Ребро 'edges'[{index}] имеет отрицательный вес; алгоритм Дейкстры неприменим.")


def solve(data):
    validate(data)
    graph = nx.DiGraph() if data.get("directed", True) else nx.Graph()
    for start_vertex, end_vertex, weight in data["edges"]:
        graph.add_edge(start_vertex, end_vertex, weight=weight)

    source = data["source"]
    target = data["target"]

    if source not in graph or target not in graph:
        raise ValueError("Начальная или конечная вершина отсутствует в графе.")

    if not nx.has_path(graph, source, target):
        print(f"Пути из вершины {source} в вершину {target} не существует.")
        return

    path = nx.shortest_path(graph, source=source, target=target, weight="weight")
    length = nx.shortest_path_length(graph, source=source, target=target, weight="weight")

    print("Кратчайший путь:", " -> ".join(map(str, path)))
    print("Длина пути:", length)


def main():
    parser = argparse.ArgumentParser(
        description="Поиск кратчайшего пути в графе (алгоритм Дейкстры)."
    )
    parser.add_argument("--input", help="Путь к JSON-файлу с данными задачи.")
    parser.add_argument("--interactive", action="store_true", help="Ввести данные вручную.")
    parser.add_argument("--dump-default", action="store_true", help="Вывести данные по умолчанию в формате JSON и выйти.")
    args = parser.parse_args()

    if args.dump_default:
        print(json.dumps(read_json(DEFAULT_DATA_PATH), ensure_ascii=False, indent=2))
        sys.exit(0)

    data = load_data(args)
    solve(data)


if __name__ == "__main__":
    main()
