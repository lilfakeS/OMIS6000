"""
@author: OMIS6000 (Winter2024) Group 12
"""

from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Create the optimization model
model = gb.Model("Bus route")

cost = [[1,2,3,4,5,6],[2,3,4,5,6,7],[3,4,5,6,7,8],[3,3,4,4,5,5]]

# Create the one class of eight decision variables 
x = model.addVars(6, 4, vtype=GRB.BINARY, name="Bus routes and companies")

# The objective function
model.setObjective(gb.quicksum((cost[i][j] * x[j, i] for i in range(4) for j in range(6))), GRB.MINIMIZE)
# Add the constraints

# One company for one route
for i in range(6):
    model.addConstr(gb.quicksum(x[i,j] for j in range(4)) <= 1)

# Two routes for one company
for j in range(4):
    model.addConstr(gb.quicksum(x[i,j] for i in range(6)) <= 2)

# At least three routes
model.addConstr(gb.quicksum(x[i,j] for i in range(6) for j in range(4)) >= 3)

# Route 2 and 5 the same
model.addConstr(gb.quicksum(x[1,j] for j in range(4)) == gb.quicksum(x[4,j] for j in range(4)))

# Route 3 or 4 the same
model.addConstr(gb.quicksum(x[2,j] for j in range(4)) + gb.quicksum(x[3,j] for j in range(4)) == 1)

# If Company B take 1, cannot take 4
model.addConstr(x[0,1] <= 1 - x[3,1])
    
# If Company A take 3, also take 5
model.addConstr(x[2,0] <= x[4,0])

# Company D at least one route
model.addConstr(gb.quicksum(x[i,3] for i in range(6)) >= 1)

# Optimally solve the problem
model.optimize()

# Print the objective and decision variables
model.printAttr('X')

# The status of the model
print("Model Status: ", model.status)
