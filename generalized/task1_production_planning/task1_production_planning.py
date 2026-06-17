import argparse
import json
import os
import sys
import pulp

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
    print("Ввод данных задачи производственного планирования.")
    number_of_products = int(input("Число видов продукции: ").strip())
    products = []
    profit = []
    demand = []
    for product_number in range(number_of_products):
        current_product_name = input(f"Название продукта {product_number + 1}: ").strip() or f"Продукт {product_number + 1}"
        products.append(current_product_name)
        current_profit = float(input(f"Прибыль за единицу '{current_product_name}': ").strip())
        profit.append(current_profit)
        current_demand = input(f"Макс. спрос на '{current_product_name}' (Enter = без ограничения на спрос): ").strip()
        demand.append(None if current_demand == "" else float(current_demand))

    number_of_resources = int(input("Число видов ресурсов: ").strip())
    resources = []
    available = []
    usage = []
    for resource_number in range(number_of_resources):
        current_resource_name = input(f"Название ресурса {resource_number + 1}: ").strip() or f"Ресурс {resource_number + 1}"
        resources.append(current_resource_name)
        current_available = float(input(f"Доступно ресурса '{current_resource_name}': ").strip())
        available.append(current_available)
        usage_row = []
        for product_number in range(number_of_products):
            usage_row.append(float(input(f"Расход '{current_resource_name}' на ед. '{products[product_number]}': ").strip()))
        usage.append(usage_row)

    return {
        "sense": "max",
        "currency": "руб.",
        "products": products,
        "profit": profit,
        "resources": resources,
        "available": available,
        "usage": usage,
        "demand": demand
    }


def validate(data):
    number_of_products = len(data["products"])
    number_of_resources = len(data["resources"])
    if len(data["profit"]) != number_of_products:
        raise ValueError("Длина 'profit' не совпадает с числом продуктов.")
    if len(data["demand"]) != number_of_products:
        raise ValueError("Длина 'demand' не совпадает с числом продуктов.")
    if len(data["available"]) != number_of_resources:
        raise ValueError("Длина 'available' не совпадает с числом ресурсов.")
    if len(data["usage"]) != number_of_resources:
        raise ValueError("Число строк 'usage' не совпадает с числом ресурсов.")
    for index, usage_row in enumerate(data["usage"]):
        if len(usage_row) != number_of_products:
            raise ValueError(f"Строка 'usage'[{index}] не совпадает с числом продуктов.")


def solve(data, integer):
    validate(data)
    number_of_products = len(data["products"])
    number_of_resources = len(data["resources"])
    currency = data.get("currency", "")

    sense = pulp.LpMaximize if data.get("sense", "max") == "max" else pulp.LpMinimize
    model = pulp.LpProblem("Production_Planning", sense)

    cat = "Integer" if integer else "Continuous"
    x = []
    for product_number in range(number_of_products):
        product_demand = data["demand"][product_number]
        var = pulp.LpVariable(f"x_{product_number}", lowBound=0, upBound=product_demand, cat=cat)
        x.append(var)

    model += pulp.lpSum(data["profit"][product_number] * x[product_number] for product_number in range(number_of_products)), "Objective"

    for resource_number in range(number_of_resources):
        model += (
            pulp.lpSum(data["usage"][resource_number][product_number] * x[product_number] for product_number in range(number_of_products)) <= data["available"][resource_number],
            data["resources"][resource_number]
        )

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    print("Статус:", pulp.LpStatus[model.status])
    print("Оптимальный план выпуска:")
    for product_number in range(number_of_products):
        product_demand = data["demand"][product_number]
        limit = "без ограничения" if product_demand is None else product_demand
        print(f"  {data['products'][product_number]} = {pulp.value(x[product_number]):.2f} (спрос: {limit})")

    obj = pulp.value(model.objective)
    label = "Максимальная прибыль" if sense == pulp.LpMaximize else "Минимум"
    print(f"{label} = {obj:.2f} {currency}")

    print("Использование ресурсов:")
    for resource_number in range(number_of_resources):
        used = sum(data["usage"][resource_number][k] * pulp.value(x[k]) for k in range(number_of_products))
        print(f"  {data['resources'][resource_number]}: {used:.2f} из {data['available'][resource_number]}")


def main():
    parser = argparse.ArgumentParser(
        description="Задача производственного планирования (линейное программирование)."
    )
    parser.add_argument("--input", help="Путь к JSON-файлу с данными задачи.")
    parser.add_argument("--interactive", action="store_true", help="Ввести данные вручную.")
    parser.add_argument("--integer", action="store_true", help="Целочисленный выпуск.")
    parser.add_argument("--dump-default", action="store_true", help="Вывести данные по умолчанию в формате JSON и выйти.")
    args = parser.parse_args()

    if args.dump_default:
        print(json.dumps(read_json(DEFAULT_DATA_PATH), ensure_ascii=False, indent=2))
        sys.exit(0)

    data = load_data(args)
    solve(data, args.integer)


if __name__ == "__main__":
    main()
