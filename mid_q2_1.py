from gurobipy import Model, GRB, quicksum
import pandas as pd
from sympy import symbols, diff, solve, sqrt

nonprofits_df=pd.read_csv('https://raw.githubusercontent.com/lilfakeS/OMIS6000/main/non_profits.csv')


# Given budget
total_budget = 50e6

# Initialize the model
m = Model('nonprofit_allocation')

# Create variables for allocation ai for each nonprofit i
allocations = m.addVars(len(nonprofits_df), name='allocations', lb=0)

# Objective function: Sum of utilities ui for each nonprofit i
# We need to add the utilities to the model using the addVar method and then set the objective using setObjective
utilities = m.addVars(len(nonprofits_df), name='utilities')

# Update the model to add the new variables
m.update()

# Define the objective function components for each nonprofit i
for i in range(len(nonprofits_df)):
    alpha_i = nonprofits_df.loc[i, 'alpha_i']
    beta_i = nonprofits_df.loc[i, 'beta_i']
    a_i = allocations[i]
    

    ei = m.addVar(name=f'effort_{i}')
    m.addConstr(utilities[i] == alpha_i*a_i + 2*sqrt(beta_i)*ei - 0.5*ei*ei)
    
    m.addConstr(ei*ei <= beta_i*a_i)

# Set the objective to maximize the sum of utilities
m.setObjective(quicksum(utilities[i] for i in range(len(nonprofits_df))), GRB.MAXIMIZE)

# Add budget constraint
m.addConstr(quicksum(allocations[i] for i in range(len(nonprofits_df))) <= total_budget, 'budget')

# Solve the model
m.optimize()

# Get the optimized allocations for each nonprofit
optimized_allocations = m.getAttr('x', allocations)

optimized_allocations


# Define the symbols
e_i, a_i, alpha_i, beta_i = symbols('e_i a_i alpha_i beta_i', real=True, positive=True)

# Define the utility function
u_i = alpha_i * a_i - (1/2) * e_i**2 + 2 * sqrt(e_i * beta_i * a_i)

# Compute the derivative of the utility function with respect to e_i
du_i_de_i = diff(u_i, e_i)

# Solve for e_i to find the effort level that maximizes the utility function
e_i_star = solve(du_i_de_i, e_i)
e_i_star


# Equation derived from setting the first derivative to zero
equation = -e_i + (beta_i * a_i) / sqrt(e_i * beta_i * a_i)

# Solve for e_i (Question b answer)
e_i_optimal = solve(equation, e_i)
print(e_i_optimal)




# Define the output function part of the utility function without the allocation utility
output_function = -1/2 * e_i**2 + 2 * sqrt(e_i * beta_i * a_i)

# Substitute e_i_star into the output function (Question c answer)
optimal_output = output_function.subs(e_i, e_i_star[0])
optimal_output.simplify()


