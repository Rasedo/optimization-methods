import pulp

model = pulp.LpProblem("Furniture_Production", pulp.LpMaximize)

x1 = pulp.LpVariable("Office", lowBound=0, cat="Continuous")
x2 = pulp.LpVariable("Premium", lowBound=0, cat="Continuous")

model += 2000 * x1 + 3500 * x2, "Total_Profit"

model += 2 * x1 + 3 * x2 <= 120, "Material"
model += 1 * x1 + 2 * x2 <= 80, "Labor"
model += x2 <= 25, "Demand"

model.solve(pulp.PULP_CBC_CMD(msg=False))

print("Статус:", pulp.LpStatus[model.status])
print(f"x1 (Офисные) = {pulp.value(x1):.2f}")
print(f"x2 (Премиум) = {pulp.value(x2):.2f}")
print(f"Максимальная прибыль = {pulp.value(model.objective):.2f} руб.")

used_material = 2 * pulp.value(x1) + 3 * pulp.value(x2)
used_labor = 1 * pulp.value(x1) + 2 * pulp.value(x2)
print(f"Израсходовано ДСП: {used_material:.2f} из 120")
print(f"Израсходовано труда: {used_labor:.2f} из 80")
