import gurobipy as gp

# Define the cost matrix C_ij
C = [[10, 12, 8, 15, 9, 11],
     [9, 13, 11, 14, 10, 12],
     [11, 10, 13, 12, 14, 9],
     [8, 11, 10, 13, 12, 10]]

# Define the number of companies and routes
num_companies = len(C)
num_routes = len(C[0])

# Create a new model
model = gp.Model("Bus Route Assignment")

# Create decision variables
x = model.addVars(num_companies, num_routes, vtype=gp.GRB.BINARY, name="x")
y = model.addVars(num_routes, vtype=gp.GRB.BINARY, name="y")

# Set objective function
model.setObjective(gp.quicksum(C[i][j] * x[i, j] for i in range(num_companies) for j in range(num_routes)), gp.GRB.MINIMIZE)

# Add constraints
# 1. Only one company can be assigned to a route if it is opened
for j in range(num_routes):
    model.addConstr(gp.quicksum(x[i, j] for i in range(num_companies)) == y[j])

# 2. Each company can be assigned to at most two bus routes
for i in range(num_companies):
    model.addConstr(gp.quicksum(x[i, j] for j in range(num_routes)) <= 2)

# 3. At least three bus routes must be opened
model.addConstr(gp.quicksum(y[j] for j in range(num_routes)) >= 3)

# 4. Route 2 and 5 must both be opened or not at all
model.addConstr(y[1] == y[4])

# 5. Either route 3 must be opened or route 4 must be opened but not both
model.addConstr(y[2] + y[3] == 1)

# 6. If company B is assigned to route 1, it cannot also provide service to route 4
model.addConstr(x[1, 0] + x[1, 3] <= 1)

# 7. If company A is assigned to route 3, it must also be assigned to route 5
model.addConstr(x[0, 2] <= x[0, 4])

# 8. Company D must be assigned to at least one route
model.addConstr(gp.quicksum(x[3, j] for j in range(num_routes)) >= 1)

# Optimize the model
model.optimize()

# Print the optimal solution
print("Optimal total cost: ", model.objVal)

print("Opened routes:")
for j in range(num_routes):
    if y[j].x > 0.5:
        print("Route", j+1, "is opened")

print("Company assignments:")
for i in range(num_companies):
    for j in range(num_routes):
        if x[i, j].x > 0.5:
            print("Company", chr(65+i), "is assigned to Route", j+1)

# The status of the model
print("Model Status: ", model.status)
