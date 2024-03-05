"""
@author: Practice Q2 - S&P
"""

from gurobipy import GRB
import gurobipy as gb
import pandas as pd

df = pd.read_csv(r"C:\Users\chiha\OneDrive - York University\Operational Research\Practice Questions\sp500_data.csv")

# Instantiate our optimization problem in
model = gb.Model("S&P investment")

#Construct decision variables for each class of decision variables
x = model.addVars(67, lb = 0, ub = 600000, vtype=GRB.CONTINUOUS, name="Investment")

# Add the objective function to the optimization problem 
model.setObjective(gb.quicksum(x[i]*df.iloc[i,5]/100 for i in range(67)), GRB.MAXIMIZE)

# Capacity constraint
model.addConstr(gb.quicksum(x[i] for i in range(67)) <= 10000000)

# Telecom investment
model.addConstr(gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Telecommunications Services'].index) <= 500000)
                   
# Information Technology
model.addConstr(gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Information Technology'].index) >= 0.75 * gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Telecommunications Services'].index))

# Difference constraint
model.addConstr((gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Consumer Discretionary'].index) - gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Consumer Staples'].index)) <= 200000)
model.addConstr((gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Consumer Discretionary'].index) - gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Consumer Staples'].index)) >= -200000)

# Energy & Headquarter
model.addConstr(gb.quicksum(x[i] for i in df[df['GICS Sector'] == 'Energy'].index) >= 1000000)
model.addConstr(gb.quicksum(x[i] for i in df[df['Location of Headquarters'].str.contains('New York, New York')].index) >= 300000)

# Optimally solve the problem
model.optimize()

# Print the objective and decision variables
model.printAttr('X')

# The status of the model
print("Model Status: ", model.status)

nyc = []

for i in df[df['Location of Headquarters'].str.contains('New York, New York')].index:
    value = x[i].X
    nyc.append(value)

print("Investment in NYC is", sum(nyc))