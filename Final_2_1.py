import gurobipy as gp
from gurobipy import GRB

# Define the data
scenarios = list(range(1, 17))
probabilities = [0.09, 0.12, 0.10, 0.05, 0.16, 0.14, 0.03, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02, 0.01]
demands = [90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165]

# Initialize the model
model = gp.Model("Coffee_Supply")

# Decision variables
x = model.addVar(name="x")  # Initial order quantity from primary supplier
y1 = model.addVars(scenarios, name="Phil_Sebastian")  # Orders from Phil & Sebastian
y2 = model.addVars(scenarios, name="Rosso")  # Orders from Rosso
y3 = model.addVars(scenarios, name="Monogram")  # Orders from Monogram
rosso_bin = model.addVars(scenarios, vtype=GRB.BINARY, name="Rosso_Binary")  # Binary for Rosso's minimum order
monogram_bin = model.addVars(scenarios, vtype=GRB.BINARY, name="Monogram_Binary")  # Binary for Monogram's minimum order

# Constraints
# Demand satisfaction constraints
demand_cons = model.addConstrs((x + y1[n] + y2[n] + y3[n] >= demands[n-1] for n in scenarios), name="demand_satisfaction")

# Minimum order constraints
rosso_min_order = model.addConstrs((y2[n] >= 70 * rosso_bin[n] for n in scenarios), name="rosso_min")
monogram_min_order = model.addConstrs((y3[n] >= 40 * monogram_bin[n] for n in scenarios), name="monogram_min")

# Objective function
model.setObjective(x * 95 + sum(probabilities[n-1] * (y1[n] * 120 + y2[n] * 105 + y3[n] * 110) for n in scenarios), GRB.MINIMIZE)

# Optimize the model
model.optimize()

# Output the solution
print(f"Total cost: ${model.objVal:.2f}")
print(f"Initial coffee order from primary supplier: {x.X} gallons")
for n in scenarios:
    print(f"Scenario {n}:")
    print(f"  Phil & Sebastian: {y1[n].X} gallons")
    print(f"  Rosso: {y2[n].X} gallons")
    print(f"  Monogram: {y3[n].X} gallons")


# Calculate the optimal solution for each scenario as if the exact demand was known in advance
ws_costs = []
for demand in demands:
    m = gp.Model("Wait_and_See")
    x_ws = m.addVar(name="x_ws")
    y1_ws = m.addVar(name="Phil_Sebastian_ws")
    y2_ws = m.addVar(name="Rosso_ws")
    y3_ws = m.addVar(name="Monogram_ws")
    
    # Constraint: satisfy exact demand
    m.addConstr(x_ws + y1_ws + y2_ws + y3_ws == demand)
    
    # Objective: Minimize cost for this scenario
    m.setObjective(95*x_ws + 120*y1_ws + 105*y2_ws + 110*y3_ws, GRB.MINIMIZE)
    
    m.optimize()
    ws_costs.append(m.objVal)

# Calculate expected WS cost
expected_ws_cost = sum(p * cost for p, cost in zip(probabilities, ws_costs))

# Calculate EVPI
evpi = expected_ws_cost - model.objVal

print(f"Expected WS Cost: {expected_ws_cost:.2f}")
print(f"EVPI: {evpi:.2f}")


# Solve using the mean demand
mean_demand = sum(p * d for p, d in zip(probabilities, demands))

m_eev = gp.Model("EEV")
x_eev = m_eev.addVar(name="x_eev")
# Assuming we order to meet the mean demand exactly
m_eev.addConstr(x_eev == mean_demand)

m_eev.setObjective(95*x_eev, GRB.MINIMIZE)
m_eev.optimize()
eev = m_eev.objVal

# VSS
vss = eev - model.objVal

print(f"EEV: {eev:.2f}")
print(f"VSS: {vss:.2f}")

threshold_price = model.objVal /x.X
print(f"Threshold price per gallon: ${threshold_price:.1f}")