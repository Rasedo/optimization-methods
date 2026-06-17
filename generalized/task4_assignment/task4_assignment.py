import argparse
import json
import os
import sys
import numpy as np
from scipy.optimize import linear_sum_assignment

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
    print("Ввод данных задачи о назначениях.")
    sense = input("Цель ('max' эффективность или 'min' затраты, Enter = 'max'): ").strip() or "max"
    size = int(input("Число исполнителей (= числу работ): ").strip())

    workers = []
    for worker_number in range(size):
        worker_name = input(f"Название исполнителя {worker_number + 1}: ").strip() or f"Сотрудник {worker_number + 1}"
        workers.append(worker_name)

    tasks = []
    for task_number in range(size):
        task_name = input(f"Название работы {task_number + 1}: ").strip() or f"Задача {task_number + 1}"
        tasks.append(task_name)

    efficiency = []
    for worker_number in range(size):
        efficiency_row = []
        for task_number in range(size):
            value = float(input(f"Оценка '{workers[worker_number]}' на '{tasks[task_number]}': ").strip())
            efficiency_row.append(value)
        efficiency.append(efficiency_row)

    return {
        "sense": sense,
        "workers": workers,
        "tasks": tasks,
        "efficiency": efficiency
    }


def validate(data):
    number_of_workers = len(data["workers"])
    number_of_tasks = len(data["tasks"])
    if number_of_workers != number_of_tasks:
        raise ValueError("Число исполнителей должно совпадать с числом работ.")
    if len(data["efficiency"]) != number_of_workers:
        raise ValueError("Число строк 'efficiency' не совпадает с числом исполнителей.")
    for index, efficiency_row in enumerate(data["efficiency"]):
        if len(efficiency_row) != number_of_tasks:
            raise ValueError(f"Строка 'efficiency'[{index}] не совпадает с числом работ.")


def solve(data):
    validate(data)
    sense = data.get("sense", "max")
    matrix = np.array(data["efficiency"], dtype=float)

    if sense == "max":
        row_indices, col_indices = linear_sum_assignment(-matrix)
    else:
        row_indices, col_indices = linear_sum_assignment(matrix)

    label = "Суммарная эффективность" if sense == "max" else "Суммарные затраты"
    print("Оптимальные назначения:")
    for worker_index, task_index in zip(row_indices, col_indices):
        value = matrix[worker_index, task_index]
        print(f"  {data['workers'][worker_index]} -> {data['tasks'][task_index]} (оценка = {value:g})")

    total = matrix[row_indices, col_indices].sum()
    print(f"{label} = {total:g}")


def main():
    parser = argparse.ArgumentParser(
        description="Задача о назначениях (венгерский алгоритм)."
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
