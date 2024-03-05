import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Read in nurse shift cost data
df = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/nurse_shift_costs.csv')

# Extract relevant data
nurses = df['Nurse_ID'].tolist()
categories = df['Category'].tolist()
weekday_costs = df['Cost_Weekday'].tolist()
weekend_costs = df['Cost_Weekend'].tolist()
overtime_costs = df['Cost_Overtime'].tolist()

# Create model
m = gp.Model('nurse_scheduling')

# Define decision variables
x = {}
for i in nurses:
    for j in range(1, 15):
        x[i,j] = m.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}')

y = {}        
for i in nurses:
    y[i] = m.addVar(vtype=GRB.BINARY, name=f'y_{i}')
    
z = {}
for i in nurses:
    for k in range(1, 12):
        z[i,k] = m.addVar(vtype=GRB.BINARY, name=f'z_{i}_{k}')

# Define objective function
m.setObjective(gp.quicksum(x[i,j] * (weekday_costs[i-1] if j%2==1 else weekend_costs[i-1]) 
                           for i in nurses for j in range(1,15)) +
               gp.quicksum(z[i,k] * overtime_costs[i-1] for i in nurses for k in range(1,12)), 
               GRB.MINIMIZE)

# Shift coverage constraints
for j in range(1, 15):
    m.addConstr(gp.quicksum(x[i,j] for i in nurses) >= 6)

# Hours worked constraints    
for i in nurses:
    m.addConstr(gp.quicksum(12*x[i,j] for j in range(1,15)) >= 36)
    m.addConstr(gp.quicksum(12*x[i,j] for j in range(1,15)) <= 60)
    
# SRN coverage constraints
for j in range(1, 15):
    m.addConstr(gp.quicksum(x[i,j] for i in nurses if categories[i-1]=='SRN') >= 1)
    
# No back-to-back shifts
for i in nurses:
    for j in range(1, 14, 2):
        m.addConstr(x[i,j] + x[i,j+1] <= 1)
        
# Overtime tracking constraints
for i in nurses:
    m.addConstr(gp.quicksum(x[i,j] for j in range(1,15)) - 3 <= 11*y[i])
    m.addConstr(gp.quicksum(z[i,k] for k in range(1,12)) == 11*y[i])
    for k in range(1, 12):
        m.addConstr(z[i,k] <= y[i])

# Optimize
m.optimize()

# Print results
print(f'Optimal objective value: ${m.objVal:.0f}')

num_overtime_shifts = sum(z[i,k].x for i in nurses for k in range(1,12))
print(f'Number of overtime shifts: {num_overtime_shifts:.0f}')