import argparse
import json
import math
import os
import sys
from scipy.stats import norm

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
    print("Ввод данных задачи управления запасами (точка заказа).")
    units = input("Единицы измерения товара (Enter = 'ед.'): ").strip() or "ед."
    time_units = input("Единицы измерения времени (Enter = 'нед.'): ").strip() or "нед."
    mean_demand = float(input("Средний спрос за период: ").strip())
    std_demand = float(input("Стандартное отклонение спроса: ").strip())
    lead_time = float(input("Время выполнения заказа (число периодов): ").strip())
    service_level = float(input("Требуемый уровень сервиса (например 0.95): ").strip())

    return {
        "units": units,
        "time_units": time_units,
        "mean_demand": mean_demand,
        "std_demand": std_demand,
        "lead_time": lead_time,
        "service_level": service_level
    }


def validate(data):
    if data["std_demand"] < 0:
        raise ValueError("Стандартное отклонение не может быть отрицательным.")
    if data["lead_time"] < 0:
        raise ValueError("Время выполнения заказа не может быть отрицательным.")
    if not 0 < data["service_level"] < 1:
        raise ValueError("Уровень сервиса должен быть в интервале (0, 1).")


def solve(data):
    validate(data)
    units = data.get("units", "")

    mean_demand = data["mean_demand"]
    std_demand = data["std_demand"]
    lead_time = data["lead_time"]
    service_level = data["service_level"]

    safety_factor = norm.ppf(service_level)
    mean_during_lead = mean_demand * lead_time
    std_during_lead = std_demand * math.sqrt(lead_time)
    safety_stock = safety_factor * std_during_lead
    reorder_point = mean_during_lead + safety_stock

    print(f"Уровень сервиса: {service_level:.2%}")
    print(f"Коэффициент надежности z = {safety_factor:.5f}")
    print(f"Средний спрос за время поставки: {mean_during_lead:.2f} {units}")
    print(f"СКО спроса за время поставки: {std_during_lead:.2f} {units}")
    print(f"Страховой запас: {safety_stock:.2f} {units}")
    print(f"Точка заказа (ROP): {reorder_point:.2f} {units}")
    print(f"Точка заказа (округление вверх): {math.ceil(reorder_point)} {units}")


def main():
    parser = argparse.ArgumentParser(
        description="Управление запасами: расчёт точки заказа (ROP)."
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
