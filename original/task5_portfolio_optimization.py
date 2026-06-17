import numpy as np
from scipy.optimize import minimize

rA = 0.12
rB = 0.08
sigmaA = 0.15
sigmaB = 0.10
rho = 0.2


def portfolio_risk(w):
    wA = w[0]
    wB = 1 - wA
    var = (wA ** 2 * sigmaA ** 2 +
           wB ** 2 * sigmaB ** 2 +
           2 * wA * wB * sigmaA * sigmaB * rho)
    return np.sqrt(var)


w0 = [0.5]
bounds = [(0, 0.8)]

result = minimize(portfolio_risk, w0, bounds=bounds)

w_opt = result.x[0]
risk_opt = result.fun
ret_opt = w_opt * rA + (1 - w_opt) * rB

print(f"Оптимальная доля в A: {w_opt:.4f} ({w_opt * 100:.2f}%)")
print(f"Минимальный риск портфеля: {risk_opt:.4f} ({risk_opt * 100:.2f}%)")
print(f"Доходность портфеля: {ret_opt:.4f} ({ret_opt * 100:.2f}%)")
