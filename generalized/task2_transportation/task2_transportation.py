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
    print("Ввод данных транспортной задачи.")
    number_of_warehouses = int(input("Число складов (поставщиков): ").strip())
    warehouses = []
    supply = []
    for warehouse_number in range(number_of_warehouses):
        current_warehouse_name = input(f"Название склада {warehouse_number + 1}: ").strip() or f"Склад {warehouse_number + 1}"
        warehouses.append(current_warehouse_name)
        current_supply = float(input(f"Запас на складе '{current_warehouse_name}': ").strip())
        supply.append(current_supply)

    number_of_stores = int(input("Число магазинов (потребителей): ").strip())
    stores = []
    demand = []
    for store_number in range(number_of_stores):
        current_store_name = input(f"Название магазина {store_number + 1}: ").strip() or f"Магазин {store_number + 1}"
        stores.append(current_store_name)
        current_demand = float(input(f"Потребность магазина '{current_store_name}': ").strip())
        demand.append(current_demand)

    cost = []
    for warehouse_number in range(number_of_warehouses):
        cost_row = []
        for store_number in range(number_of_stores):
            cost_value = float(input(f"Стоимость доставки '{warehouses[warehouse_number]}' -> '{stores[store_number]}': ").strip())
            cost_row.append(cost_value)
        cost.append(cost_row)

    return {
        "currency": "руб.",
        "warehouses": warehouses,
        "supply": supply,
        "stores": stores,
        "demand": demand,
        "cost": cost
    }


def validate(data):
    number_of_warehouses = len(data["warehouses"])
    number_of_stores = len(data["stores"])
    if len(data["supply"]) != number_of_warehouses:
        raise ValueError("Длина 'supply' не совпадает с числом складов.")
    if len(data["demand"]) != number_of_stores:
        raise ValueError("Длина 'demand' не совпадает с числом магазинов.")
    if len(data["cost"]) != number_of_warehouses:
        raise ValueError("Число строк 'cost' не совпадает с числом складов.")
    for index, cost_row in enumerate(data["cost"]):
        if len(cost_row) != number_of_stores:
            raise ValueError(f"Строка 'cost'[{index}] не совпадает с числом магазинов.")


def solve(data, integer):
    validate(data)
    number_of_warehouses = len(data["warehouses"])
    number_of_stores = len(data["stores"])
    currency = data.get("currency", "")

    total_supply = sum(data["supply"])
    total_demand = sum(data["demand"])

    model = pulp.LpProblem("Transportation", pulp.LpMinimize)

    cat = "Integer" if integer else "Continuous"
    x = pulp.LpVariable.dicts(
        "ship",
        (range(number_of_warehouses), range(number_of_stores)),
        lowBound=0,
        cat=cat
    )

    model += pulp.lpSum(
        data["cost"][warehouse_number][store_number] * x[warehouse_number][store_number]
        for warehouse_number in range(number_of_warehouses)
        for store_number in range(number_of_stores)
    ), "Total_Cost"

    supply_is_equality = total_supply <= total_demand
    demand_is_equality = total_demand <= total_supply

    for warehouse_number in range(number_of_warehouses):
        shipped_from_warehouse = pulp.lpSum(x[warehouse_number][store_number] for store_number in range(number_of_stores))
        if supply_is_equality:
            model += shipped_from_warehouse == data["supply"][warehouse_number], f"supply_{warehouse_number}"
        else:
            model += shipped_from_warehouse <= data["supply"][warehouse_number], f"supply_{warehouse_number}"

    for store_number in range(number_of_stores):
        shipped_to_store = pulp.lpSum(x[warehouse_number][store_number] for warehouse_number in range(number_of_warehouses))
        if demand_is_equality:
            model += shipped_to_store == data["demand"][store_number], f"demand_{store_number}"
        else:
            model += shipped_to_store <= data["demand"][store_number], f"demand_{store_number}"

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    print("Статус:", pulp.LpStatus[model.status])
    if total_supply != total_demand:
        print(f"Внимание: задача несбалансирована (запасы {total_supply}, спрос {total_demand}).")
    print("Оптимальный план перевозок:")
    for warehouse_number in range(number_of_warehouses):
        for store_number in range(number_of_stores):
            shipped = pulp.value(x[warehouse_number][store_number])
            if shipped and shipped > 0:
                print(f"  {data['warehouses'][warehouse_number]} -> {data['stores'][store_number]}: {shipped:.0f}")

    obj = pulp.value(model.objective)
    print(f"Минимальные затраты = {obj:.2f} {currency}")


def main():
    parser = argparse.ArgumentParser(
        description="Транспортная задача (линейное программирование)."
    )
    parser.add_argument("--input", help="Путь к JSON-файлу с данными задачи.")
    parser.add_argument("--interactive", action="store_true", help="Ввести данные вручную.")
    parser.add_argument("--integer", action="store_true", help="Целочисленные перевозки.")
    parser.add_argument("--dump-default", action="store_true", help="Вывести данные по умолчанию в формате JSON и выйти.")
    args = parser.parse_args()

    if args.dump_default:
        print(json.dumps(read_json(DEFAULT_DATA_PATH), ensure_ascii=False, indent=2))
        sys.exit(0)

    data = load_data(args)
    solve(data, args.integer)


if __name__ == "__main__":
    main()
