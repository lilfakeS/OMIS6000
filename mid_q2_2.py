from gurobipy import Model, GRB, quicksum
import pandas as pd
from sympy import symbols, diff, solve, sqrt

non_profits_df=pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/non_profits.csv')

# Initialize the Gurobi model
model = Model("Nonprofit_Optimization")

# Parameters from the CSV file
alpha = non_profits_df['alpha_i'].values
beta = non_profits_df['beta_i'].values
N = len(alpha)  # Number of non-profits

# The budget for the allocation (as per problem statement, say 50 million)
budget = 50e6

# Decision variables
# Allocation amount for each nonprofit
a = model.addVars(N, name="a", lb=0)

# Auxiliary variables for the nonlinear term (β_i * a_i)^(1/3)
# We will use piecewise-linear functions to approximate the nonlinear term with 1500 pieces as suggested
x = model.addVars(N, name="x")
for i in range(N):
    model.addGenConstrPow(x[i], a[i], 1/3, name="power_constr_{}".format(i))

# The objective is to maximize the sum of outputs from all non-profits
# Output for each nonprofit is β_i * a_i^(1/3)
model.setObjective(quicksum(beta[i] * x[i] for i in range(N)), GRB.MAXIMIZE)

# Budget constraint: The sum of all allocations should be less than or equal to the budget
model.addConstr(quicksum(a[i] for i in range(N)) <= budget, "budget")

# We now optimize the model
model.optimize()

# Retrieve the optimal values of allocation amounts
optimal_allocations = model.getAttr('x', a)

# Calculate the optimal effort levels e_i^* for each nonprofit
# According to the problem statement, e_i^* = (β_i * a_i)^1/3
optimal_efforts = [(beta[i] * optimal_allocations[i])**(1/3) for i in range(N)]

# Display the optimal allocations and efforts
optimal_allocations, optimal_efforts, model.objVal
expected_output_value = model.objVal
print(expected_output_value)
