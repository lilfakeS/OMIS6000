"""
@author: Xia Sheng, Zhirong Huang, Jiacheng Peng (2023)
"""

import pandas as pd
from gurobipy import GRB
import gurobipy as gb

#import data 
data = pd.read_excel("/Users/justinsheng/Downloads/A1 combine.xlsx", sheet_name=None)
direct_capacity = data['Capacity_for_Direct_Production_'].set_index('ProductionFacility')['Capacity'].to_dict()
# Transshipment production capacity
transship_capacity = data['Capacity_for_Transship_Producti'].set_index('ProductionFacility')['Capacity'].to_dict()
# Distribution center capacities
dist_center_capacity = data['Capacity_for_Transship_Distribu'].set_index('TransshipmentHub')['Capacity'].to_dict()
# Direct shipment costs
cost_direct = data['Cost_Production_to_Refinement'].set_index(['ProductionFacility', 'RefinementCenter'])['Cost'].to_dict()
# Transshipment costs
cost_transship = data['Cost_Transshipment_to_Refinemen'].set_index(['TransshipmentHub', 'RefinementCenter'])['Cost'].to_dict()
# Demand at refinement centers
demand = data['Refinement_Demand'].set_index('RefinementCenter')['Demand'].to_dict()

#(a),(b)
# Create the optimization model
model = gb.Model("Can2Oil Optimization")

# Create decision variables for direct shipments
x = model.addVars(25, 5, lb=0, vtype=GRB.CONTINUOUS, name="Direct_Shipment")
# Create decision variables for transshipment
y = model.addVars(15, 2, 5, lb=0, vtype=GRB.CONTINUOUS, name="Transshipment")

#The objective function for transshipment
direct_objective = gb.quicksum(cost_direct[i+1, j+1]*x[i, j] for i in range(25) for j in range(5))
trans_objective = gb.quicksum((cost_transship[j+1, k+1])*y[i, j, k] for i in range(15) for j in range(2) for k in range(5))
model.setObjective(direct_objective + trans_objective, GRB.MINIMIZE)

# Add supply constraints for direct shipments
for i in range(25):
    model.addConstr(gb.quicksum(x[i, j] for j in range(5)) <= direct_capacity[i+1], name=f"Direct_Supply_Constraint_{i+1}")

# Add supply constraints for transshipment production
for i in range(15):
    model.addConstr(gb.quicksum(y[i, j, k] for j in range(2) for k in range(5)) <= transship_capacity[i+1], name=f"Transship_Supply_Constraint_{i+1}")

# Add capacity constraints for distribution centers
for j in range(2):
    model.addConstr(gb.quicksum(y[i, j, k] for i in range(15) for k in range(5)) <= dist_center_capacity[j+1], name=f"Dist_Center_Capacity_{j+1}")

# Add demand constraints
for k in range(5):
    model.addConstr(gb.quicksum(x[i, k] for i in range(25)) + gb.quicksum(y[i, j, k] for i in range(15) for j in range(2)) >= demand[k+1], name=f"Demand_Constraint_{k+1}")

# Optimally solve the problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found.")
    print(f"Total Cost: {model.objVal}")
    print("Direct Shipment Quantities:")
    for i in range(25):
        for j in range(5):
            if x[i, j].x > 0:
                print(f"From Production Facility {i+1} to Refinement Center {j+1}: {x[i, j].x} million pounds")

    print("\nTransshipment Quantities:")
    total_transshipment = 0
    for i in range(15):
        for j in range(2):
            for k in range(5):
                if y[i, j, k].x > 0:
                    transshipment_amount = y[i, j, k].x
                    print(f"From Production Facility {i+26} through Transshipment Hub {j+1} to Refinement Center {k+1}: {y[i, j, k].x} million pounds")
                    total_transshipment += transshipment_amount
    
    # Print total transshipment amount
    print(f"\nTotal Transshipment Amount: {total_transshipment} million pounds")

else:
    print("Optimal solution not found.")


#(c)
#import data 
data = pd.read_excel("/Users/justinsheng/Downloads/A1 combine.xlsx", sheet_name=None)
direct_capacity = data['Capacity_for_Direct_Production_'].set_index('ProductionFacility')['Capacity'].to_dict()
# Transshipment production capacity
transship_capacity = data['Capacity_for_Transship_Producti'].set_index('ProductionFacility')['Capacity'].to_dict()
# Distribution center capacities
dist_center_capacity = data['Capacity_for_Transship_Distribu'].set_index('TransshipmentHub')['Capacity'].to_dict()
# Direct shipment costs
cost_direct = data['Cost_Production_to_Refinement'].set_index(['ProductionFacility', 'RefinementCenter'])['Cost'].to_dict()
# Transshipment costs
cost_transship = data['Cost_Transshipment_to_Refinemen'].set_index(['TransshipmentHub', 'RefinementCenter'])['Cost'].to_dict()
# Demand at refinement centers
demand = data['Refinement_Demand'].set_index('RefinementCenter')['Demand'].to_dict()
# Create the optimization model
model = gb.Model("Can2Oil Optimization_2")

# Assuming penalty factor for transshipment
penalty_factor = 10  # You can adjust this value

# Create decision variables for direct shipments
x = model.addVars(25, 5, lb=0, vtype=GRB.CONTINUOUS, name="Direct_Shipment")
# Create decision variables for transshipment
y = model.addVars(15, 2, 5, lb=0, vtype=GRB.CONTINUOUS, name="Transshipment")

# Modify the objective function to include the penalty for transshipment
direct_objective = gb.quicksum(cost_direct[i+1, j+1]*x[i, j] for i in range(25) for j in range(5))
trans_objective = gb.quicksum((cost_transship[j+1, k+1] + penalty_factor)*y[i, j, k] for i in range(15) for j in range(2) for k in range(5))
model.setObjective(direct_objective + trans_objective, GRB.MINIMIZE)

# Add supply constraints for direct shipments
for i in range(25):
    model.addConstr(gb.quicksum(x[i, j] for j in range(5)) <= direct_capacity[i+1], name=f"Direct_Supply_Constraint_{i+1}")

# Add supply constraints for transshipment production
for i in range(15):
    model.addConstr(gb.quicksum(y[i, j, k] for j in range(2) for k in range(5)) <= transship_capacity[i+1], name=f"Transship_Supply_Constraint_{i+1}")

# Add capacity constraints for distribution centers
for j in range(2):
    model.addConstr(gb.quicksum(y[i, j, k] for i in range(15) for k in range(5)) <= dist_center_capacity[j+1], name=f"Dist_Center_Capacity_{j+1}")

# Add demand constraints
for k in range(5):
    model.addConstr(gb.quicksum(x[i, k] for i in range(25)) + gb.quicksum(y[i, j, k] for i in range(15) for j in range(2)) >= demand[k+1], name=f"Demand_Constraint_{k+1}")

# Optimally solve the problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found.")
    print(f"Total Cost: {model.objVal}")
    print("Direct Shipment Quantities:")
    for i in range(25):
        for j in range(5):
            if x[i, j].x > 0:
                print(f"From Production Facility {i+1} to Refinement Center {j+1}: {x[i, j].x} million pounds")

    print("\nTransshipment Quantities:")
    total_transshipment = 0
    for i in range(15):
        for j in range(2):
            for k in range(5):
                if y[i, j, k].x > 0:
                    transshipment_amount = y[i, j, k].x
                    print(f"From Production Facility {i+26} through Transshipment Hub {j+1} to Refinement Center {k+1}: {y[i, j, k].x} million pounds")
                    total_transshipment += transshipment_amount
    
    # Print total transshipment amount
    print(f"\nTotal Transshipment Amount: {total_transshipment} million pounds")

else:
    print("Optimal solution not found.")


#(d)
#import data 
data = pd.read_excel("/Users/justinsheng/Downloads/A1 combine.xlsx", sheet_name=None)
direct_capacity = data['Capacity_for_Direct_Production_'].set_index('ProductionFacility')['Capacity'].to_dict()
# Transshipment production capacity
transship_capacity = data['Capacity_for_Transship_Producti'].set_index('ProductionFacility')['Capacity'].to_dict()
# Distribution center capacities
dist_center_capacity = data['Capacity_for_Transship_Distribu'].set_index('TransshipmentHub')['Capacity'].to_dict()
# Direct shipment costs
cost_direct = data['Cost_Production_to_Refinement'].set_index(['ProductionFacility', 'RefinementCenter'])['Cost'].to_dict()
# Transshipment costs
cost_transship = data['Cost_Transshipment_to_Refinemen'].set_index(['TransshipmentHub', 'RefinementCenter'])['Cost'].to_dict()
# Demand at refinement centers
demand = data['Refinement_Demand'].set_index('RefinementCenter')['Demand'].to_dict()
# Create the optimization model
model = gb.Model("Can2Oil Optimization_2")

# Assuming maximum ratio of transshipment
max_ratio = 0.3 

# Create decision variables for direct shipments
x = model.addVars(25, 5, lb=0, vtype=GRB.CONTINUOUS, name="Direct_Shipment")
# Create decision variables for transshipment
y = model.addVars(15, 2, 5, lb=0, vtype=GRB.CONTINUOUS, name="Transshipment")

# The objective function for transshipment
direct_objective = gb.quicksum(cost_direct[i+1, j+1]*x[i, j] for i in range(25) for j in range(5))
trans_objective = gb.quicksum((cost_transship[j+1, k+1])*y[i, j, k] for i in range(15) for j in range(2) for k in range(5))
model.setObjective(direct_objective + trans_objective, GRB.MINIMIZE)

# Add supply constraints for direct shipments
for i in range(25):
    model.addConstr(gb.quicksum(x[i, j] for j in range(5)) <= direct_capacity[i+1], name=f"Direct_Supply_Constraint_{i+1}")

# Add supply constraints for transshipment production
for i in range(15):
    model.addConstr(gb.quicksum(y[i, j, k] for j in range(2) for k in range(5)) <= transship_capacity[i+1], name=f"Transship_Supply_Constraint_{i+1}")

# Add capacity constraints for distribution centers
for j in range(2):
    model.addConstr(gb.quicksum(y[i, j, k] for i in range(15) for k in range(5)) <= dist_center_capacity[j+1], name=f"Dist_Center_Capacity_{j+1}")

# Add demand constraints
for k in range(5):
    model.addConstr(gb.quicksum(x[i, k] for i in range(25)) + gb.quicksum(y[i, j, k] for i in range(15) for j in range(2)) >= demand[k+1], name=f"Demand_Constraint_{k+1}")

# Add new constraint to limit the proportion of transshipped oil
total_direct_shipment = gb.quicksum(x[i, j] for i in range(25) for j in range(5))
total_transship_shipment = gb.quicksum(y[i, j, k] for i in range(15) for j in range(2) for k in range(5))
model.addConstr(total_transship_shipment <= max_ratio * (total_direct_shipment + total_transship_shipment), "TransshipmentProportionConstraint")

# Optimally solve the problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found.")
    print(f"Total Cost: {model.objVal}")
    print("Direct Shipment Quantities:")
    for i in range(25):
        for j in range(5):
            if x[i, j].x > 0:
                print(f"From Production Facility {i+1} to Refinement Center {j+1}: {x[i, j].x} million pounds")

    print("\nTransshipment Quantities:")
    total_transshipment = 0
    for i in range(15):
        for j in range(2):
            for k in range(5):
                if y[i, j, k].x > 0:
                    transshipment_amount = y[i, j, k].x
                    print(f"From Production Facility {i+26} through Transshipment Hub {j+1} to Refinement Center {k+1}: {y[i, j, k].x} million pounds")
                    total_transshipment += transshipment_amount
    
    # Print total transshipment amount
    print(f"\nTotal Transshipment Amount: {total_transshipment} million pounds")

else:
    print("Optimal solution not found.")


#(f)
#import data 
data = pd.read_excel("/Users/justinsheng/Downloads/A1 combine.xlsx", sheet_name=None)
direct_capacity = data['Capacity_for_Direct_Production_'].set_index('ProductionFacility')['Capacity'].to_dict()
# Transshipment production capacity
transship_capacity = data['Capacity_for_Transship_Producti'].set_index('ProductionFacility')['Capacity'].to_dict()
# Distribution center capacities
dist_center_capacity = data['Capacity_for_Transship_Distribu'].set_index('TransshipmentHub')['Capacity'].to_dict()
# Direct shipment costs
cost_direct = data['Cost_Production_to_Refinement'].set_index(['ProductionFacility', 'RefinementCenter'])['Cost'].to_dict()
# Transshipment costs
cost_transship = data['Cost_Transshipment_to_Refinemen'].set_index(['TransshipmentHub', 'RefinementCenter'])['Cost'].to_dict()
# Demand at refinement centers
demand = data['Refinement_Demand'].set_index('RefinementCenter')['Demand'].to_dict()

#(a),(b)
# Create the optimization model
model = gb.Model("Can2Oil Optimization")

# Create decision variables for direct shipments
x = model.addVars(25, 5, lb=0, vtype=GRB.CONTINUOUS, name="Direct_Shipment")
# Create decision variables for transshipment
y = model.addVars(15, 2, 5, lb=0, vtype=GRB.CONTINUOUS, name="Transshipment")

#The objective function for transshipment
direct_objective = gb.quicksum(cost_direct[i+1, j+1]*x[i, j] for i in range(25) for j in range(5))
trans_objective = gb.quicksum((cost_transship[j+1, k+1])*y[i, j, k] for i in range(15) for j in range(2) for k in range(5))
model.setObjective(direct_objective + trans_objective, GRB.MINIMIZE)

# Add supply constraints for direct shipments
for i in range(25):
    model.addConstr(gb.quicksum(x[i, j] for j in range(5)) <= direct_capacity[i+1], name=f"Direct_Supply_Constraint_{i+1}")

# Add supply constraints for transshipment production
for i in range(15):
    model.addConstr(gb.quicksum(y[i, j, k] for j in range(2) for k in range(5)) <= transship_capacity[i+1], name=f"Transship_Supply_Constraint_{i+1}")

# Add capacity constraints for distribution centers
for j in range(2):
    model.addConstr(gb.quicksum(y[i, j, k] for i in range(15) for k in range(5)) <= dist_center_capacity[j+1], name=f"Dist_Center_Capacity_{j+1}")

# Add demand constraints
for k in range(5):
    model.addConstr(gb.quicksum(x[i, k] for i in range(25)) + gb.quicksum(y[i, j, k] for i in range(15) for j in range(2)) >= demand[k+1], name=f"Demand_Constraint_{k+1}")

# Define the indices of the production facilities closer to North America
closer_producers_indices = set(range(1, 16))

# Define the function to check if a producer is closer to North America
def is_closer_producer(producer_index):
    return producer_index in closer_producers_indices


# Assuming a minimum sourcing requirement from closer producers
min_sourcing_requirement = 0.7 

# Add sourcing constraints
total_sourcing = gb.quicksum(x[i, j] for i in range(25) for j in range(5))
sourcing_from_closer_producers = gb.quicksum(x[i, j] for i in range(25) for j in range(5) if is_closer_producer(i+1))
model.addConstr(sourcing_from_closer_producers >= min_sourcing_requirement * total_sourcing, "MinSourcingFromCloserProducers")


# Optimally solve the problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found.")
    print(f"Total Cost: {model.objVal}")
    print("Direct Shipment Quantities:")
    for i in range(25):
        for j in range(5):
            if x[i, j].x > 0:
                print(f"From Production Facility {i+1} to Refinement Center {j+1}: {x[i, j].x} million pounds")

    print("\nTransshipment Quantities:")
    total_transshipment = 0
    for i in range(15):
        for j in range(2):
            for k in range(5):
                if y[i, j, k].x > 0:
                    transshipment_amount = y[i, j, k].x
                    print(f"From Production Facility {i+26} through Transshipment Hub {j+1} to Refinement Center {k+1}: {y[i, j, k].x} million pounds")
                    total_transshipment += transshipment_amount
    
    # Print total transshipment amount
    print(f"\nTotal Transshipment Amount: {total_transshipment} million pounds")

else:
    print("Optimal solution not found.")