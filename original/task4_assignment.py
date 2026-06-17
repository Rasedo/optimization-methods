import numpy as np
from scipy.optimize import linear_sum_assignment

cost_matrix = np.array([[9, 2, 7, 8],
                        [6, 4, 3, 7],
                        [5, 8, 1, 9],
                        [7, 6, 5, 4]])

row_ind, col_ind = linear_sum_assignment(-cost_matrix)

print("Решение венгерским алгоритмом (SciPy):")
for i, j in zip(row_ind, col_ind):
    print(f"Сотрудник {i + 1} -> Задача {j + 1}, эффективность = {cost_matrix[i, j]}")
total = cost_matrix[row_ind, col_ind].sum()
print(f"Суммарная эффективность = {total}")


import pulp

prob = pulp.LpProblem("Assignment", pulp.LpMaximize)
x = pulp.LpVariable.dicts("x", (range(4), range(4)), cat="Binary")

prob += pulp.lpSum(cost_matrix[i][j] * x[i][j] for i in range(4) for j in range(4))

for i in range(4):
    prob += pulp.lpSum(x[i][j] for j in range(4)) == 1
for j in range(4):
    prob += pulp.lpSum(x[i][j] for i in range(4)) == 1

prob.solve(pulp.PULP_CBC_CMD(msg=False))

print("\nРешение целочисленным программированием (PuLP):")
for i in range(4):
    for j in range(4):
        if pulp.value(x[i][j]) > 0.5:
            print(f"Сотрудник {i + 1} -> Задача {j + 1}, эффективность = {cost_matrix[i, j]}")
print(f"Суммарная эффективность = {pulp.value(prob.objective):.0f}")
