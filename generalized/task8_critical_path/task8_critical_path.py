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
    print("Ввод данных задачи сетевого планирования (метод критического пути).")
    time_units = input("Единицы измерения времени (Enter = 'дней'): ").strip() or "дней"
    number_of_tasks = int(input("Число работ: ").strip())

    tasks = []
    for task_number in range(number_of_tasks):
        name = input(f"Название работы {task_number + 1}: ").strip() or f"Работа {task_number + 1}"
        duration = float(input(f"Длительность работы '{name}': ").strip())
        predecessors_raw = input(f"Предшественники '{name}' (через пробел, Enter = нет): ").strip()
        predecessors = predecessors_raw.split() if predecessors_raw else []
        tasks.append({"name": name, "duration": duration, "predecessors": predecessors})

    return {
        "time_units": time_units,
        "tasks": tasks
    }


def validate(data):
    names = [task["name"] for task in data["tasks"]]
    if len(names) != len(set(names)):
        raise ValueError("Названия работ должны быть уникальными.")
    known = set(names)
    for task in data["tasks"]:
        for predecessor in task["predecessors"]:
            if predecessor not in known:
                raise ValueError(f"Работа '{task['name']}' ссылается на неизвестного предшественника '{predecessor}'.")


def solve(data):
    validate(data)
    time_units = data.get("time_units", "")
    tasks = {task["name"]: task for task in data["tasks"]}

    graph = nx.DiGraph()
    for name, task in tasks.items():
        graph.add_node(name, duration=task["duration"])
        for predecessor in task["predecessors"]:
            graph.add_edge(predecessor, name)

    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Сетевой график содержит цикл; критический путь не определён.")

    order = list(nx.topological_sort(graph))

    early_start = {}
    early_finish = {}
    for node in order:
        predecessors = list(graph.predecessors(node))
        early_start[node] = 0 if not predecessors else max(early_finish[predecessor] for predecessor in predecessors)
        early_finish[node] = early_start[node] + tasks[node]["duration"]

    project_duration = max(early_finish.values())

    late_finish = {}
    late_start = {}
    for node in reversed(order):
        successors = list(graph.successors(node))
        late_finish[node] = project_duration if not successors else min(late_start[successor] for successor in successors)
        late_start[node] = late_finish[node] - tasks[node]["duration"]

    critical = [node for node in order if abs(late_start[node] - early_start[node]) < 1e-9]

    print(f"Длительность проекта: {project_duration:g} {time_units}")
    print("Критический путь:", " -> ".join(critical))
    print("Параметры работ (ES / EF / LS / LF / Резерв):")
    for node in order:
        slack = late_start[node] - early_start[node]
        print(f"  {node}: ES={early_start[node]:g}, EF={early_finish[node]:g}, "
              f"LS={late_start[node]:g}, LF={late_finish[node]:g}, Резерв={slack:g}")


def main():
    parser = argparse.ArgumentParser(
        description="Сетевое планирование: метод критического пути (CPM)."
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
