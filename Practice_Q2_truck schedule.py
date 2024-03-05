"""
@author: OMIS6000 (Winter2024) Group 12
"""

from gurobipy import GRB
import gurobipy as gb
import pandas as pd

# Create the optimization model
model = gb.Model("Truck usage")

cost = [5500, 4700, 3900]

# Create the one class of eight decision variables 
x = model.addVars(3, 3, vtype=GRB.BINARY, name="Trucks and Numbers")
y = model.addVars(7, 9, vtype=GRB.BINARY, name="Heavy pallets")
z = model.addVars(6, 9, vtype=GRB.BINARY, name="Medium pallets")
w = model.addVars(5, 9, vtype=GRB.BINARY, name="Light pallets")

# The objective function
model.setObjective(gb.quicksum(cost[i] * x[i, j] for i in range(3) for j in range(3)), GRB.MINIMIZE)

# At least one type of truck
for i in range(3):
    model.addConstr(gb.quicksum(x[i,j] for j in range(3)) >= 1)

# Each package to be delivered
for i in range(7):
    model.addConstr(gb.quicksum(y[i,j] for j in range(9)) ==1 )
for i in range(6):
    model.addConstr(gb.quicksum(z[i,j] for j in range(9)) ==1 )
for i in range(5):
    model.addConstr(gb.quicksum(w[i,j] for j in range(9)) ==1 )

# eqch truck within load
# heavy truck
for j in range(3):
    model.addConstr(gb.quicksum(y[i,j] for i in range(7)) * 4 + gb.quicksum(z[i,j] for i in range(6)) * 3 + gb.quicksum(w[i,j] for i in range(5)) * 0.5 <= 13.5)
for j in range(3,6):
    model.addConstr(gb.quicksum(y[i,j] for i in range(7)) * 4 + gb.quicksum(z[i,j] for i in range(6)) * 3 + gb.quicksum(w[i,j] for i in range(5)) * 0.5 <= 12)
for j in range(6,9):
    model.addConstr(gb.quicksum(y[i,j] for i in range(7)) * 4 + gb.quicksum(z[i,j] for i in range(6)) * 3 + gb.quicksum(w[i,j] for i in range(5)) * 0.5 <= 10)

# joining truck and the pallets
for j in range(3):
    for i in range(7):
        model.addConstr(y[i,j] <= x[0,j])
    for i in range(6):
        model.addConstr(z[i,j] <= x[0,j])
    for i in range(5):
        model.addConstr(w[i,j] <= x[0,j])
for j in range(3,6):
    for i in range(7):
        model.addConstr(y[i,j] <= x[1,j-3])
    for i in range(6):
        model.addConstr(z[i,j] <= x[1,j-3])
    for i in range(5):
        model.addConstr(w[i,j] <= x[1,j-3])
for j in range(6,9):
    for i in range(7):
        model.addConstr(y[i,j] <= x[2,j-6])
    for i in range(6):
        model.addConstr(z[i,j] <= x[2,j-6])
    for i in range(5):
        model.addConstr(w[i,j] <= x[2,j-6])

# Optimally solve the problem
model.optimize()

# Print the objective and decision variables
model.printAttr('X')

# The status of the model
print("Model Status: ", model.status)
