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
m = gp.Model("OptiDiet")

# Create decision variables
x = m.addVars(120, vtype=gp.GRB.CONTINUOUS, name="x")

# Nutritional balance constraints
for i in range(len(nutrient_requirements)):
    nutrient = nutrient_requirements.iloc[i]['Nutrient']
    min_req = nutrient_requirements.iloc[i]['Min_Requirement']
    max_req = nutrient_requirements.iloc[i]['Max_Requirement']
    m.addConstr(gp.quicksum(nutrient_content.iloc[j][nutrient] * x[j] for j in range(120)) >= min_req,
                f"Min_{nutrient}")
    m.addConstr(gp.quicksum(nutrient_content.iloc[j][nutrient] * x[j] for j in range(120)) <= max_req,
                f"Max_{nutrient}")


# Dietary preference constraints
for category in ['Veggie', 'Vegan', 'Kosher', 'Halal']:
    m.addConstr(gp.quicksum(x[i] for i in range(120) if food_categories.iloc[i][f"Is_{category}"] == 1) >=
                food_preferences.iloc[0][f"{category.lower()}_grams"], f"{category}_constraint")

# Variety constraints
total_grams = food_preferences.iloc[0]['All_grams']
for i in range(120):
    m.addConstr(x[i] <= 0.03 * total_grams, f"Variety_{i}")

# Objective function
m.setObjective(gp.quicksum(food_categories.iloc[i]['Cost_per_gram'] * x[i] for i in range(120)), gp.GRB.MINIMIZE)

# Solve the model
m.optimize()

# Print the optimal solution
print(f"Optimal cost: {m.objVal:.2f}")

# Proportion of Halal and Kosher foods
halal_kosher_grams = sum(x[i].x for i in range(120) if food_categories.iloc[i]['Is_Halal'] == 1 or food_categories.iloc[i]['Is_Kosher'] == 1)
total_grams = sum(x[i].x for i in range(120))
print(f"Proportion of Halal and Kosher foods: {halal_kosher_grams / total_grams:.2f}")

# Omit variety constraints and resolve
m.remove(m.getConstrs())
m.optimize()
print(f"Optimal cost without variety constraints: {m.objVal:.2f}")
print(f"Number of non-zero variables without variety constraints: {len([v for v in m.getVars() if v.x > 0])}")

# Increase dietary preference constraints by 10,000 grams
for category in ['Veggie', 'Vegan', 'Kosher', 'Halal', 'All']:
    m.getConstrByName(f"{category}_constraint").RHS += 10000
m.optimize()
print(f"Optimal cost with increased dietary preferences: {m.objVal:.2f}")

# Reduced cost for Food_1
print(f"Reduced cost for Food_1: {m.getVarByName('x[0]').RC:.2f}")