"""
@author: Xia Sheng (2023)
"""

import pandas as pd
from gurobipy import GRB
import gurobipy as gp


# Read data from CSV files
food_categories = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/food_categories.csv')
food_preferences = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/food_preferences.csv')
nutrient_content = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/nutrient_content.csv')
nutrient_requirements = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/nutrient_requirements.csv')


# Create a new model
model = gp.Model("OptiDiet")

# Create decision variables
x = model.addVars(food_categories.shape[0], vtype=gp.GRB.CONTINUOUS, name="x")

# Set objective function
model.setObjective(gp.quicksum(food_categories['Cost_per_gram'][i] * x[i] for i in range(food_categories.shape[0])), gp.GRB.MINIMIZE)

# Add nutritional balance constraints
for j in range(nutrient_requirements.shape[0]):
    model.addConstr(gp.quicksum(nutrient_content.iloc[i, j+1] * x[i] for i in range(food_categories.shape[0])) >= nutrient_requirements.iloc[j, 1], f"min_nutrient_{j}")
    model.addConstr(gp.quicksum(nutrient_content.iloc[i, j+1] * x[i] for i in range(food_categories.shape[0])) <= nutrient_requirements.iloc[j, 2], f"max_nutrient_{j}")

# Add dietary preference constraints (Q3 answer)
model.addConstr(gp.quicksum(food_categories['Is_Vegetarian'][i] * x[i] for i in range(food_categories.shape[0])) >= food_preferences['Veggie_grams'][0], "veggie_constraint")
model.addConstr(gp.quicksum(food_categories['Is_Vegan'][i] * x[i] for i in range(food_categories.shape[0])) >= food_preferences['Vegan_grams'][0], "vegan_constraint")
model.addConstr(gp.quicksum(food_categories['Is_Kosher'][i] * x[i] for i in range(food_categories.shape[0])) >= food_preferences['Kosher_grams'][0], "kosher_constraint")
model.addConstr(gp.quicksum(food_categories['Is_Halal'][i] * x[i] for i in range(food_categories.shape[0])) >= food_preferences['Halal_grams'][0], "halal_constraint")
model.addConstr(gp.quicksum(x[i] for i in range(food_categories.shape[0])) == food_preferences['All_grams'][0], "all_constraint")


# Add variety constraints (Q4 answer)
for i in range(food_categories.shape[0]):
    model.addConstr(x[i] <= 0.03 * food_preferences['All_grams'][0], f"variety_constraint_{i}")

# Optimize the model
model.optimize()

# Print the optimal solution
if model.status == gp.GRB.OPTIMAL:
    print("Optimal solution found!")
    for i in range(food_categories.shape[0]):
        print(f"{food_categories['Food_Item'][i]}: {x[i].x} grams")
    print(f"Total cost: ${model.objVal:.2f}")
else:
    print("No optimal solution found.")


# 1
x = model.addVars(food_categories.shape[0], vtype=gp.GRB.CONTINUOUS, name="x")
print(x)

