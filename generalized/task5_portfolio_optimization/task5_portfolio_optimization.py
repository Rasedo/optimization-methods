import argparse
import json
import os
import sys
import numpy as np
from scipy.optimize import minimize

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
    print("Ввод данных задачи оптимизации портфеля.")
    number_of_assets = int(input("Число активов: ").strip())

    assets = []
    returns = []
    volatility = []
    min_weight = []
    max_weight = []
    for asset_number in range(number_of_assets):
        asset_name = input(f"Название актива {asset_number + 1}: ").strip() or f"Актив {asset_number + 1}"
        assets.append(asset_name)
        returns.append(float(input(f"Ожидаемая доходность '{asset_name}' (доля, напр. 0.12): ").strip()))
        volatility.append(float(input(f"Риск (СКО) '{asset_name}' (доля, напр. 0.15): ").strip()))
        minimum = input(f"Мин. доля '{asset_name}' (Enter = 0): ").strip()
        maximum = input(f"Макс. доля '{asset_name}' (Enter = 1): ").strip()
        min_weight.append(0.0 if minimum == "" else float(minimum))
        max_weight.append(1.0 if maximum == "" else float(maximum))

    correlation = []
    print("Матрица корреляций (по строкам):")
    for first_asset in range(number_of_assets):
        correlation_row = []
        for second_asset in range(number_of_assets):
            if first_asset == second_asset:
                correlation_row.append(1.0)
            elif second_asset < first_asset:
                correlation_row.append(correlation[second_asset][first_asset])
            else:
                value = float(input(f"Корреляция '{assets[first_asset]}' и '{assets[second_asset]}': ").strip())
                correlation_row.append(value)
        correlation.append(correlation_row)

    return {
        "assets": assets,
        "returns": returns,
        "volatility": volatility,
        "correlation": correlation,
        "max_weight": max_weight,
        "min_weight": min_weight
    }


def validate(data):
    number_of_assets = len(data["assets"])
    if len(data["returns"]) != number_of_assets:
        raise ValueError("Длина 'returns' не совпадает с числом активов.")
    if len(data["volatility"]) != number_of_assets:
        raise ValueError("Длина 'volatility' не совпадает с числом активов.")
    if len(data["correlation"]) != number_of_assets:
        raise ValueError("Число строк 'correlation' не совпадает с числом активов.")
    for index, correlation_row in enumerate(data["correlation"]):
        if len(correlation_row) != number_of_assets:
            raise ValueError(f"Строка 'correlation'[{index}] не совпадает с числом активов.")
    if len(data.get("min_weight", [])) not in (0, number_of_assets):
        raise ValueError("Длина 'min_weight' не совпадает с числом активов.")
    if len(data.get("max_weight", [])) not in (0, number_of_assets):
        raise ValueError("Длина 'max_weight' не совпадает с числом активов.")


def build_covariance(volatility, correlation):
    volatility = np.array(volatility, dtype=float)
    correlation = np.array(correlation, dtype=float)
    return np.outer(volatility, volatility) * correlation


def solve(data):
    validate(data)
    number_of_assets = len(data["assets"])
    returns = np.array(data["returns"], dtype=float)
    covariance = build_covariance(data["volatility"], data["correlation"])

    min_weight = data.get("min_weight") or [0.0] * number_of_assets
    max_weight = data.get("max_weight") or [1.0] * number_of_assets
    bounds = list(zip(min_weight, max_weight))

    def portfolio_variance(weights):
        return float(weights @ covariance @ weights)

    constraints = [{"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0}]
    initial_guess = np.array([1.0 / number_of_assets] * number_of_assets)

    result = minimize(
        portfolio_variance,
        initial_guess,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    weights = result.x
    risk = np.sqrt(result.fun)
    expected_return = float(weights @ returns)

    print("Оптимальные доли активов:")
    for asset_number in range(number_of_assets):
        print(f"  {data['assets'][asset_number]}: {weights[asset_number]:.4f} ({weights[asset_number] * 100:.2f}%)")
    print(f"Минимальный риск портфеля: {risk:.4f} ({risk * 100:.2f}%)")
    print(f"Ожидаемая доходность портфеля: {expected_return:.4f} ({expected_return * 100:.2f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Оптимизация портфеля: минимизация риска (квадратичное программирование)."
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
