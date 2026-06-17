import math
from scipy.stats import norm

mean_demand = 50
std_demand = 10
lead_time = 3
service_level = 0.95

z = norm.ppf(service_level)

mean_during_lead = mean_demand * lead_time
std_during_lead = std_demand * math.sqrt(lead_time)
safety_stock = z * std_during_lead
rop = mean_during_lead + safety_stock

print(f"Коэффициент надежности z = {z:.5f}")
print(f"Средний спрос за время поставки: {mean_during_lead:.2f}")
print(f"Страховой запас: {safety_stock:.2f}")
print(f"Точка заказа (ROP): {rop:.2f}")
