import gurobipy as gb

# Data
probabilities = [0.09, 0.12, 0.10, 0.05, 0.16, 0.14, 0.03, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02, 0.01]
demands = [90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165]

# Model
m = gb.Model('Coffee_Supply_Optimization')

# Decision variables
x = m.addVar(name="x")  # Coffee gallons from primary supplier
y1 = m.addVars(16, name="Phil&Sebastian")  # Gallons from Phil & Sebastian
y2 = m.addVars(16, name="Rosso")  # Gallons from Rosso
y3 = m.addVars(16, name="Monogram")  # Gallons from Monogram

# Objective function
m.setObjective(95*x + gb.quicksum(probabilities[n] * (120*y1[n] + 105*y2[n] + 110*y3[n]) for n in range(16)), gb.GRB.MINIMIZE)

# Constraints
demand_constraints = m.addConstrs((x + y1[n] + y2[n] + y3[n] >= demands[n] for n in range(16)), name="Demand")
minimum_order_rosso = m.addConstrs((y2[n] >= 70 for n in range(16)), name="MinOrderRosso")
minimum_order_monogram = m.addConstrs((y3[n] >= 40 for n in range(16)), name="MinOrderMonogram")

# Solve
m.optimize()

# Output results
if m.status == gb.GRB.OPTIMAL:
    print(f"Total cost: {m.objVal:.2f}")
    print(f"Coffee ordered from primary supplier: {x.X} gallons")
    for n in range(16):
        print(f"Scenario {n+1}:")
        print(f"  Phil & Sebastian: {y1[n].X} gallons")
        print(f"  Rosso: {y2[n].X} gallons")
        print(f"  Monogram: {y3[n].X} gallons")
