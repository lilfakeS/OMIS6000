"""
@author: Practice Q1 (2024 Winter)
"""

from gurobipy import GRB
import gurobipy as gb

# Create the optimization model
model = gb.Model("Transportation Problem")

# A list of list of costs
costs = [[0.05,0.06,0.07,0.08,0.09,0.10],[0.08,0.05,0.09,0.10,0.07,0.06]]
Supply = [100000 , 250000]

# Create the a single class of decision variables
x = model.addVars(2, 29, lb=0, vtype=GRB.CONTINUOUS, name="Transportation Plan")

# The objective function
model.setObjective(
    gb.quicksum((costs[i][0] * x[i, j] for i in range(2) for j in range(5))) +
    gb.quicksum((costs[i][1] * x[i, k] for i in range(2) for k in range(5, 10))) +
    gb.quicksum((costs[i][2] * x[i, l] for i in range(2) for l in range(10, 15))) +
    gb.quicksum((costs[i][3] * x[i, m] for i in range(2) for m in range(15, 20))) +
    gb.quicksum((costs[i][4] * x[i, n] for i in range(2) for n in range(20, 25))) +
    gb.quicksum((costs[i][5] * x[i, o] for i in range(2) for o in range(25, 29))),
    GRB.MINIMIZE
)


# Add the supply constraints
for i in range(2):
    model.addConstr(gb.quicksum(x[i,j] for j in range(29)) == Supply[i], name="Supply Constraint %i" %i)

# Add the demand constraints
for j in range(7):
    model.addConstr(gb.quicksum(x[i,j] for i in range(2)) == 4*350000/(22+7*4), name="hospital Constraint")
for j in range(7,29):
    model.addConstr(gb.quicksum(x[i,j] for i in range(2)) == 350000/(22+7*4), name="site Constraint")

model.addConstr(gb.quicksum(x[0,j] for j in range(5)) - gb.quicksum(x[1,j] for j in range(5)) <= 4800, name="Difference Constraint")
model.addConstr(gb.quicksum(x[0,j] for j in range(5)) - gb.quicksum(x[1,j] for j in range(5)) >= -4800, name="Difference Constraint")

model.addConstr(gb.quicksum(x[1,j] for j in range(20,25)) <= 8 * gb.quicksum(x[0,j] for j in range(10,15)), name="Difference Constraint")

model.addConstr(gb.quicksum(x[0,j] for j in range(25,29)) >= 0.8 * gb.quicksum(x[1,j] for j in range(15,20)), name="Difference Constraint")

# Optimally solve the problem
model.optimize()

# Number of variables in the model
print("Number of Decision Variables: ", model.numVars)

# Value of the objective function
print("Total Transportation cost: ", model.objVal)

# Print the decision variables
print(model.printAttr('X'))