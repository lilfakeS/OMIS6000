"""
@author: Practice Q3
"""

import pandas as pd
from gurobipy import GRB
import gurobipy as gb

hub1 = [20,25]
hub2 = [30,45]
hub3 = [20,35]
hub4 = [30]
hub5 = [25,15,28]
hub6 = [12]
hub7 = [27]

# Create the optimization model
model = gb.Model("Bike transfer")

# Create the one class of eight decision variables 
x = model.addVars(2, lb=0, vtype=GRB.INTEGER, name="from 1 to 2/5")
y = model.addVars(2, lb=0, vtype=GRB.INTEGER, name="from 2 to 5/7")
z = model.addVars(2, lb=0, vtype=GRB.INTEGER, name="from 3 to 1/6")
w = model.addVar(lb=0, vtype=GRB.INTEGER, name="from 4 to 2")
p = model.addVars(3, lb=0, vtype=GRB.INTEGER, name="from 5 to 3/4/6")
q = model.addVar(lb=0, vtype=GRB.INTEGER, name="from 6 to 7")
r = model.addVar(lb=0, vtype=GRB.INTEGER, name="from 7 to 4")

# The objective function
model.setObjective(
    (gb.quicksum(hub1[i]*x[i] for i in range(2)))
    + (gb.quicksum(hub2[i]*y[i] for i in range(2)))
    + (gb.quicksum(hub3[i]*z[i] for i in range(2)))
    + (hub4[0] * w)
    + (gb.quicksum(hub5[i]*p[i] for i in range(3)))
    + (hub6[0] * q)
    + (hub7[0] * r), GRB.MINIMIZE)


model.addConstr(gb.quicksum(y[i] for i in range(2)) + gb.quicksum(z[i] for i in range(2)) <= 2 * (w + gb.quicksum(p[i] for i in range(3))), "not exceed twice")

model.addConstr(((
    gb.quicksum(x[i] for i in range(2)) + 
    gb.quicksum(y[i] for i in range(2)) + 
    gb.quicksum(z[i] for i in range(2)) + 
    w + 
    gb.quicksum(p[i] for i in range(3))) 
    >= 1400*0.05), "more than 5%")

model.addConstr(((
    gb.quicksum(x[i] for i in range(2)) + 
    gb.quicksum(y[i] for i in range(2)) + 
    gb.quicksum(z[i] for i in range(2)) + 
    w + 
    gb.quicksum(p[i] for i in range(3))) 
    <= 1400*0.5), "less than 50%")

# hub 1 movement
model.addConstr(z[0] - gb.quicksum(x[i] for i in range(2)) == 0.08 * 1400)

# hub 2 movement
model.addConstr(x[0] + w - gb.quicksum(y[i] for i in range(2)) == -0.05 * 1400)

# hub 3 movement
model.addConstr(p[0] - gb.quicksum(z[i] for i in range(2)) == -0.03 * 1400)

# hub 4 movement
model.addConstr(p[1] + r - w == 0.03 * 1400)

# hub 5 movement
model.addConstr(x[1] + y[0] - gb.quicksum(p[i] for i in range(3)) == -0.02 * 1400)

# hub 6 movement
model.addConstr((z[1] + p[2] - q) == +0.05 * 1400)

# hub 7 movement
model.addConstr((y[1] + q - r) == -0.06 * 1400)

# Optimally solve the problem
model.optimize()

# Print the objective and decision variables
model.printAttr('X')

# The status of the model
print("Model Status: ", model.status)
