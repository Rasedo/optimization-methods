import pulp

supply = [50, 40]
demand = [30, 30, 30]
cost = [[2, 3, 4],
        [3, 2, 5]]

warehouses = range(len(supply))
stores = range(len(demand))

prob = pulp.LpProblem("Transportation", pulp.LpMinimize)

x = pulp.LpVariable.dicts("ship", (warehouses, stores), lowBound=0, cat="Continuous")

prob += pulp.lpSum(cost[i][j] * x[i][j] for i in warehouses for j in stores)

for i in warehouses:
    prob += pulp.lpSum(x[i][j] for j in stores) == supply[i]

for j in stores:
    prob += pulp.lpSum(x[i][j] for i in warehouses) == demand[j]

prob.solve(pulp.PULP_CBC_CMD(msg=False))

print("Статус:", pulp.LpStatus[prob.status])
names = ["A", "B"]
for i in warehouses:
    for j in stores:
        print(f"Склад {names[i]} -> Магазин {j + 1}: {pulp.value(x[i][j]):.0f}")
print("Минимальные затраты =", pulp.value(prob.objective), "руб.")
