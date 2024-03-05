"""
@author: Practice Q3
"""

import pandas as pd
from gurobipy import GRB
import gurobipy as gb

route = pd.read_csv(r"https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/Routes.csv")

# Create the optimization model
model = gb.Model("Shuttle Service")

# Create the one class of eight decision variables 
x = model.addVars(58, vtype=GRB.BINARY, name="route")
y = model.addVars(58, 58, vtype=GRB.BINARY, name="glendon")
z = model.addVars(6, vtype=GRB.BINARY, name="more than three")

# The objective function
model.setObjective(
    (gb.quicksum(route.iloc[i,1]*x[i] for i in range(58)))
    + (gb.quicksum(350*y[i,j] for i in range(58) for j in range(58)))
    - (gb.quicksum(50*z[i] for i in range(6))), GRB.MINIMIZE)

route_list = ['a','b','c','d','e','f']


for j in range(6):
    model.addConstr(gb.quicksum(x[i] for i in route[route['Routes'].apply(lambda x: route_list[j] in x)].index) >= 1 + 2*z[j], "at least 1")

glendon = route[route['Routes'].apply(lambda x: 'a' in x)].index

for i in range(58):
    for j in range(58):
        if (i not in glendon) or (j not in glendon):
            model.addConstr(y[i,j] == 0)
        elif i <= j:
            model.addConstr(y[i,j] == 0)
        elif i > j:
            model.addConstr(y[i,j] <= x[i])
            model.addConstr(y[i,j] <= x[j])
            model.addConstr(y[i,j] >= x[i] + x[j] - 1)

# Optimally solve the problem
model.optimize()

# Print the objective and decision variables
model.printAttr('X')

# The status of the model
print("Model Status: ", model.status)
