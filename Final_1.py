import gurobipy as gb
from gurobipy import GRB
import pandas as pd

# Load data
supply_data = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/ecogreen_energy_supply.csv')
demand_data = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/ecogreen_energy_demand.csv')

# Initialize the model
m = gb.Model('EcoGreen_Energy_Expansion')

# Variables
# Binary variables for opening plants at sites
open_plant = m.addVars(supply_data['Plant Location'], vtype=GRB.BINARY, name="open")

# Continuous variables for the amount of energy sent from each plant to each province
energy_transferred = m.addVars(supply_data['Plant Location'], demand_data['Province Index'],
                               vtype=GRB.CONTINUOUS, name="transfer")

# Constraints
# Capacity constraints
capacity_constraints = m.addConstrs((energy_transferred.sum(p, '*') <= supply_data.loc[supply_data['Plant Location'] == p, 'Capacity'].values[0] * open_plant[p]
                                     for p in supply_data['Plant Location']), name="capacity")

# Demand fulfillment constraints for each province
demand_constraints = m.addConstrs((energy_transferred.sum('*', p) >= demand_data.loc[demand_data['Province Index'] == p, 'Demand'].values[0]
                                   for p in demand_data['Province Index']), name="demand")

# Logical and regional constraints based on problem description
# For example: If a plant at site 10 is open, sites 15 and 20 cannot be open, and vice versa
m.addConstr(open_plant[10] + open_plant[15] + open_plant[20] <= 1)

# Specific constraints based on plant dependencies
# Constraint for site 3
m.addConstr(open_plant[3] <= open_plant[4], name="dependency_3_4")
m.addConstr(open_plant[3] <= open_plant[5], name="dependency_3_5")

# Constraint for site 5
m.addConstr(open_plant[5] <= open_plant[8] + open_plant[9], name="dependency_5_8_9")

# Minimum energy output constraints
region_A = list(range(1, 11))
region_B = list(range(11, 21))
m.addConstr(sum(open_plant[i] for i in region_A) <= 2 * sum(open_plant[j] for j in region_B))

# Total energy output from sites 1-5 must be at least 30% of the total from all sites
m.addConstr(sum(energy_transferred.sum(i, '*') for i in region_A[:5]) >=
            0.3 * sum(energy_transferred.sum(k, '*') for k in supply_data['Plant Location']))

# Max supply constraint: No single power plant can provide more than 50% of a province's energy needs
max_supply_constraints = m.addConstrs((energy_transferred[i, j] <= 0.5 * demand_data.loc[demand_data['Province Index'] == j, 'Demand'].values[0]
                                      for i in supply_data['Plant Location'] for j in demand_data['Province Index']), name="max_supply")

# Objective: Minimize total cost
cost = sum(supply_data.loc[supply_data['Plant Location'] == p, 'Fixed'].values[0] * open_plant[p] + 
           sum(energy_transferred[p, j] * supply_data.loc[supply_data['Plant Location'] == p, 'Province {}'.format(j)].values[0]
               for j in demand_data['Province Index'])
           for p in supply_data['Plant Location'])
m.setObjective(cost, GRB.MINIMIZE)

# Optimize
m.optimize()

# Display results
if m.status == GRB.OPTIMAL:
    print(f"Total cost: {m.objVal:.2f}")
    for v in m.getVars():
        if v.x > 1e-6:  # Display non-zero variables
            print(f"{v.varName} = {v.x}")
else:
    print("Optimal solution not found.")

m.getVars()
