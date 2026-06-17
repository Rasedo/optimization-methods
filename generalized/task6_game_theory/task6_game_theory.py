import argparse
import json
import os
import sys
import numpy as np
from scipy.optimize import linprog

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
    print("Ввод данных матричной игры с нулевой суммой.")
    number_of_rows = int(input("Число стратегий игрока A (строки): ").strip())
    number_of_cols = int(input("Число стратегий игрока B (столбцы): ").strip())

    row_strategies = []
    for row_number in range(number_of_rows):
        name = input(f"Название стратегии A №{row_number + 1}: ").strip() or f"А{row_number + 1}"
        row_strategies.append(name)

    col_strategies = []
    for col_number in range(number_of_cols):
        name = input(f"Название стратегии B №{col_number + 1}: ").strip() or f"Б{col_number + 1}"
        col_strategies.append(name)

    payoff = []
    for row_number in range(number_of_rows):
        payoff_row = []
        for col_number in range(number_of_cols):
            value = float(input(f"Выигрыш A: '{row_strategies[row_number]}' против '{col_strategies[col_number]}': ").strip())
            payoff_row.append(value)
        payoff.append(payoff_row)

    return {
        "row_player": "A",
        "col_player": "B",
        "row_strategies": row_strategies,
        "col_strategies": col_strategies,
        "payoff": payoff
    }


def validate(data):
    number_of_rows = len(data["row_strategies"])
    number_of_cols = len(data["col_strategies"])
    if len(data["payoff"]) != number_of_rows:
        raise ValueError("Число строк 'payoff' не совпадает с числом стратегий A.")
    for index, payoff_row in enumerate(data["payoff"]):
        if len(payoff_row) != number_of_cols:
            raise ValueError(f"Строка 'payoff'[{index}] не совпадает с числом стратегий B.")


def solve(data):
    validate(data)
    payoff = np.array(data["payoff"], dtype=float)
    number_of_rows, number_of_cols = payoff.shape

    shift = 0.0
    minimum_value = payoff.min()
    if minimum_value <= 0:
        shift = -minimum_value + 1.0
    shifted = payoff + shift

    objective_row = np.zeros(number_of_rows + 1)
    objective_row[-1] = -1.0

    inequality_row = np.zeros((number_of_cols, number_of_rows + 1))
    for col_number in range(number_of_cols):
        for row_number in range(number_of_rows):
            inequality_row[col_number, row_number] = -shifted[row_number, col_number]
        inequality_row[col_number, -1] = 1.0
    inequality_bound_row = np.zeros(number_of_cols)

    equality_row = np.zeros((1, number_of_rows + 1))
    equality_row[0, :number_of_rows] = 1.0
    equality_bound_row = np.array([1.0])

    bounds_row = [(0, None)] * number_of_rows + [(None, None)]

    result_row = linprog(
        objective_row,
        A_ub=inequality_row, b_ub=inequality_bound_row,
        A_eq=equality_row, b_eq=equality_bound_row,
        bounds=bounds_row, method="highs"
    )

    objective_col = np.zeros(number_of_cols + 1)
    objective_col[-1] = 1.0

    inequality_col = np.zeros((number_of_rows, number_of_cols + 1))
    for row_number in range(number_of_rows):
        for col_number in range(number_of_cols):
            inequality_col[row_number, col_number] = shifted[row_number, col_number]
        inequality_col[row_number, -1] = -1.0
    inequality_bound_col = np.zeros(number_of_rows)

    equality_col = np.zeros((1, number_of_cols + 1))
    equality_col[0, :number_of_cols] = 1.0
    equality_bound_col = np.array([1.0])

    bounds_col = [(0, None)] * number_of_cols + [(None, None)]

    result_col = linprog(
        objective_col,
        A_ub=inequality_col, b_ub=inequality_bound_col,
        A_eq=equality_col, b_eq=equality_bound_col,
        bounds=bounds_col, method="highs"
    )

    row_strategy = result_row.x[:number_of_rows]
    col_strategy = result_col.x[:number_of_cols]
    game_value = result_row.x[-1] - shift

    print(f"Оптимальная смешанная стратегия игрока {data['row_player']}:")
    for row_number in range(number_of_rows):
        print(f"  {data['row_strategies'][row_number]}: {row_strategy[row_number]:.4f}")
    print(f"Оптимальная смешанная стратегия игрока {data['col_player']}:")
    for col_number in range(number_of_cols):
        print(f"  {data['col_strategies'][col_number]}: {col_strategy[col_number]:.4f}")
    print(f"Цена игры: {game_value:.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="Матричная игра двух лиц с нулевой суммой (сведение к ЛП)."
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
