# tutorial from https://gist.github.com/WPettersson/287de1e739d4d7869d555fd28ac587cf

# Use python3
import cplex

# Create instance of linear problem to solve
p = cplex.Cplex()

# Want max of objective
p.objective.set_sense(p.objective.sense.maximize)

# Names of vars
vars = ["x", "y", "z"]

# Coefficients of objetive function
obj = [5., 2., -1.]

# Lower bounds >= 0
l_bounds = [0., 0., 0.]

# Upper bounds (default is cplex.infinity=1e20)
u_bounds = [100,1000, cplex.infinity]

p.variables.add(obj = obj,
                lb = l_bounds,
                ub = u_bounds,
                names = vars)

#############
# Constraints
#############

constraint_names = ["c1", "c2"]

# Add actual constraints
# 3x + y -z
constraint1 = [["x", "y", "z"], [3., 1., -1.]]
# 3x + 4y + 4z (["x", "y", "z"] == [0,1,2])
constraint2 = [[0,1,2], [3., 4., 4.]]

constraints = [constraint1, constraint2]

# Add RHS
rhs = [75., 160.]

# Enter senses of constraints
# L: <=
# G: >=
# E: =
constraint_senses = ["L", "L"]

# add constraints
p.linear_constraints.add(lin_expr = constraints,
                         senses = constraint_senses,
                         rhs = rhs, 
                         names = constraint_names)

# solve
p.solve()
# print
print(p.solution.get_values())
