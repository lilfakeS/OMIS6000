from gurobipy import Model, GRB
import numpy as np
import pandas as pd

sp500_data = pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/sp500_data.csv')

# Initialize the model
model = Model("Optimal Investment Portfolio")

# Total budget for investment
total_budget = 10_000_000

# Number of stocks
n_stocks = sp500_data.shape[0]

# Investment variables: amount of money invested in each stock
investments = model.addVars(n_stocks, name="Investment", lb=0, ub=600_000)

# Objective: Maximize total expected return
expected_returns = sp500_data['PercentReturn'].values / 100  # Convert percentage to proportion
model.setObjective(sum(investments[i] * expected_returns[i] for i in range(n_stocks)), GRB.MAXIMIZE)

# Constraint 1: Total investment constraint
model.addConstr(sum(investments[i] for i in range(n_stocks)) == total_budget, "Total_Investment")

# Additional constraints based on sectors and other requirements

# Mapping sectors to investments
sectors = sp500_data['GICS Sector'].unique()
sector_investment = {sector: sum(investments[i] for i in range(n_stocks) if sp500_data['GICS Sector'][i] == sector) for sector in sectors}

# Constraint 2: Telecommunications sector investment limit
model.addConstr(sector_investment['Telecommunications Services'] <= 500_000, "Telecom_Investment_Limit")

# Constraint 3: IT sector investment at least 75% of Telecommunications sector investment
model.addConstr(sector_investment['Information Technology'] >= 0.75 * sector_investment['Telecommunications Services'], "IT_Telecom_Relationship")

# Constraint 4: Absolute difference in Consumer sectors investment
model.addConstr((sector_investment['Consumer Discretionary'] - sector_investment['Consumer Staples']) <= 200_000, "Consumer_Sectors_Difference_1")
model.addConstr((sector_investment['Consumer Discretionary'] - sector_investment['Consumer Staples']) >= -200_000, "Consumer_Sectors_Difference_2")

# Constraint 5a: At least $1 million in the Energy sector
model.addConstr(sector_investment['Energy'] >= 1_000_000, "Minimum_Energy_Investment")

# Constraint 5b: At least $300,000 in companies headquartered in New York, New York
ny_investment = sum(investments[i] for i in range(n_stocks) if sp500_data['Location of Headquarters'][i] == 'New York, New York')
model.addConstr(ny_investment >= 300_000, "Minimum_NY_Investment")

# Solving the model
model.optimize()

# Checking if the model was solved
if model.status == GRB.OPTIMAL:
    investment_solution = {sp500_data['Ticker symbol'][i]: investments[i].X for i in range(n_stocks)}
    total_expected_return = model.ObjVal
    print("Optimal total expected return:", total_expected_return)
    print("Investment solution:", investment_solution)
else:
    print("The model could not be solved to optimality.")

# Assuming your model is solved and is named 'model'
if model.status == GRB.OPTIMAL:
    # Iterate through the constraints
    for constraint in model.getConstrs():
        print(f"Shadow price for {constraint.ConstrName}: {constraint.Pi}")


