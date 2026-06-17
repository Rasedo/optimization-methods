import numpy as np
from scipy.optimize import linprog

payoff = np.array([[3, -1, 2],
                   [1, 4, -2],
                   [2, 0, 1]])

num_strategies = payoff.shape[0]
num_cols = num_strategies + 1

c = np.zeros(num_cols)
c[-1] = -1

A_ub = np.zeros((payoff.shape[1], num_cols))
for j in range(payoff.shape[1]):
    for i in range(num_strategies):
        A_ub[j, i] = -payoff[i, j]
    A_ub[j, -1] = 1
b_ub = np.zeros(payoff.shape[1])

A_eq = np.zeros((1, num_cols))
A_eq[0, :num_strategies] = 1
b_eq = np.array([1])

bounds = [(0, None)] * num_strategies + [(None, None)]

result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

x_opt = result.x[:num_strategies]
v_opt = result.x[-1]

print("Оптимальная стратегия игрока A:", x_opt)
print("Цена игры (v): ", v_opt)

cB = np.zeros(payoff.shape[1] + 1)
cB[-1] = 1

A_ubB = np.zeros((payoff.shape[0], payoff.shape[1] + 1))
for i in range(payoff.shape[0]):
    for j in range(payoff.shape[1]):
        A_ubB[i, j] = payoff[i, j]
    A_ubB[i, -1] = -1
b_ubB = np.zeros(payoff.shape[0])

A_eqB = np.zeros((1, payoff.shape[1] + 1))
A_eqB[0, :payoff.shape[1]] = 1
b_eqB = np.array([1])

boundsB = [(0, None)] * payoff.shape[1] + [(None, None)]

resultB = linprog(cB, A_ub=A_ubB, b_ub=b_ubB, A_eq=A_eqB, b_eq=b_eqB, bounds=boundsB, method="highs")

y_opt = resultB.x[:payoff.shape[1]]
w_opt = resultB.x[-1]

print("Оптимальная стратегия игрока B:", y_opt)
print("Цена игры (w): ", w_opt)
