
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


# Define the indices of the production facilities closer to North America
closer_producers_indices = set(range(1, 16))

# Define the function to check if a producer is closer to North America
def is_closer_producer(producer_index):
    return producer_index in closer_producers_indices


# Create decision variables for direct shipments
x = model.addVars(25, 5, lb=0, vtype=GRB.CONTINUOUS, name="Direct_Shipment")
# Create decision variables for transshipment
y = model.addVars(15, 2, 5, lb=0, vtype=GRB.CONTINUOUS, name="Transshipment")

# Assuming a discount factor for closer producers
discount_factor = 0.9  # e.g., 10% discount

# Modify the objective function
# Apply discount to transportation costs from closer producers
model.setObjective(
    gb.quicksum((cost_direct[i+1, j+1] * discount_factor if is_closer_producer(i+1) else cost_direct[i+1, j+1]) * x[i, j] 
                for i in range(25) for j in range(5)) +
    gb.quicksum(cost_transship[j+1, k+1]*y[i, j, k] for i in range(15) for j in range(2) for k in range(5)),
    GRB.MINIMIZE)


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

