from gurobipy import Model, GRB

# Assuming you have defined the price-response functions d_j(p_n) and d_r(p_n)
# You would need the actual functional forms to proceed with defining these functions
def d_j(p_n, max_demand_j, slope_j, previous_price):
    return max_demand_j - slope_j * (p_n - previous_price)

def d_r(p_n, max_demand_r, slope_r, previous_price):
    return max_demand_r - slope_r * (p_n - previous_price)

# Given data
max_demands_j = {1: 66, 2: 76, 3: 116, 4: 86, 5: 56, 6: 46}
max_demands_r = {1: 72, 2: 70, 3: 123, 4: 93, 5: 51, 6: 41}
slopes_j = {1: 14, 2: 13, 3: 11, 4: 8, 5: 24, 6: 28}
slopes_r = {1: 15, 2: 12, 3: 13, 4: 8, 5: 20, 6: 42}

# Create new model
m = Model("DonutPricing")

# Add price variables for each hour
p_j = m.addVars(6, lb=0, vtype=GRB.CONTINUOUS, name="p_j")
p_r = m.addVars(6, lb=0, vtype=GRB.CONTINUOUS, name="p_r")

# Add decision variables for quantities, tied to the price-response functions
q_j = m.addVars(6, lb=0, vtype=GRB.CONTINUOUS, name="q_j")
q_r = m.addVars(6, lb=0, vtype=GRB.CONTINUOUS, name="q_r")

# Objective function
profit = sum((p_j[n] - 0.92) * q_j[n] + (p_r[n] - 0.66) * q_r[n] for n in range(6))
m.setObjective(profit, GRB.MAXIMIZE)

# Supply constraints
m.addConstr(sum(q_j[n] for n in range(6)) <= 137, "SupplyConstraintJellyFilled")
m.addConstr(sum(q_r[n] for n in range(6)) <= 111, "SupplyConstraintRegular")

# Price increase constraints
for n in range(1, 6):
    m.addConstr(p_j[n] >= p_j[n-1], f"PriceIncreaseJellyFilled{n}")
    m.addConstr(p_r[n] >= p_r[n-1], f"PriceIncreaseRegular{n}")

# Quantity decrease constraints
for n in range(1, 6):
    m.addConstr(q_j[n] <= q_j[n-1], f"QuantityDecreaseJellyFilled{n}")
    m.addConstr(q_r[n] <= q_r[n-1], f"QuantityDecreaseRegular{n}")

# Jelly-filled price at least 5% higher than regular price constraint
for n in range(6):
    m.addConstr(p_j[n] >= 1.05 * p_r[n], f"JellyFilledPricePremium{n}")

# Define the price-response function constraints
for n in range(6):
    # Assume you have the previous prices p_j_0 and p_r_0 from hour before 6 pm, if not, they should be defined
    p_j_0 = 2.99  # Assuming this is the starting price
    p_r_0 = 2.99  # Assuming this is the starting price
    m.addConstr(q_j[n] == d_j(p_j[n], max_demands_j[n+1], slopes_j[n+1], p_j_0), f"DemandFuncJelly{n}")
    m.addConstr(q_r[n] == d_r(p_r[n], max_demands_r[n+1], slopes_r[n+1], p_r_0), f"DemandFuncRegular{n}")

# Optimize the model
m.optimize()

# Display the solution
if m.status == GRB.OPTIMAL:
    # Display the solution
    for n in range(6):
        print(f"Hour {n+6} pm - Price of jelly-filled 2-pack: ${p_j[n].X:.2f}, Quantity sold: {q_j[n].X}")
        print(f"Hour {n+6} pm - Price of regular 2-pack: ${p_r[n].X:.2f}, Quantity sold: {q_r[n].X}")
else:
    print("Optimization was not successful. The model did not find an optimal solution.")

