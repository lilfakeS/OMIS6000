from gurobipy import Model, GRB

# Given data
F = [25000] * 8 + [50000] * 10  # Fixed costs per location
C = [0.4, 0.4, 0.4, 0.35, 0.35, 0.35, 0.3, 0.3, 0.3, 0.25, 0.25, 0.25, 0.2, 0.2, 0.2, 0.15, 0.15, 0.15]  # Variable costs per tree

# Create a new model
m = Model("tree_planting")

# Add variables
x = m.addVars(18, vtype=GRB.INTEGER, lb=0, name="x")  # Number of trees planted
y = m.addVars(18, vtype=GRB.BINARY, name="y")        # Binary decision for location choice

# Set objective function
m.setObjective(sum(F[i] * y[i] + C[i] * x[i] for i in range(18)), GRB.MINIMIZE)

# Add constraints
m.addConstr(sum(x[i] for i in range(18)) == 10000000, "TotalTrees")           # Constraint (1)
m.addConstrs((x[i] >= 103000 * y[i] for i in range(18)), "MinTrees")          # Constraints (2)
m.addConstrs((x[i] <= 970000 * y[i] for i in range(18)), "MaxTrees")          # Constraints (3)
m.addConstr(sum(y[i] for i in range(4)) <= 2, "Group1Locations")              # Constraint (4)
m.addConstr(sum(y[i] for i in [5, 8, 11, 14, 17]) == 3, "Group2Locations")    # Constraint (5)
m.addConstr(sum(y[i] for i in [1, 3, 5, 7, 11, 13, 15, 17]) <= 4, "Group3Locations")  # Constraint (6)
m.addConstr(y[4] <= 1 - y[5], "ExcludeSite6")                                 # Constraint (7)
m.addConstr(y[4] <= 1 - y[6], "ExcludeSite7")                                 # Constraint (8)
m.addConstr(y[4] <= 1 - y[7], "ExcludeSite8")                                 # Constraint (9)
m.addConstr(2 * y[8] <= y[12] + y[14] + y[16], "IncludeWithSite9")            # Constraint (10)
m.addConstr(sum(x[i] for i in range(9)) == sum(x[i] for i in range(9, 18)), "BalanceTrees")  # Constraint (11)

# Optimize the model
m.optimize()

# Print the solution
for i in range(18):
    print(f"Location {i+1}: Plant {x[i].X} trees, Selected: {'Yes' if y[i].X > 0.5 else 'No'}")
