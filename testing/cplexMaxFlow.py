# Max Flow example

# Flow moves to the right
#      2
#   1-----3
# 4/ \     \3
# /   \     \
#s     \1    t
# \     \   /
# 5\     \ /2
#   2-----4 
#      4
# Nodes {s,1,2,3,4,t}
# Edges {s1(4), 13(2), 3t(3), 14(1), s2(5), 24(4), 4t(2)}
# Problem
# max_x x_{s1} + x_{s2}
#        (Conservation)             (Capacity)
# s.t. x_{s1} = x_{13} + x_{14}     x_{s1} <= 4
#      x_{s2} = x_{24}              x_{s2} <= 5
#      x_{13} = x_{3t}              x_{13} <= 2
#      x_{14} + x_{24} = x_{4t}     x_{14} <= 1
#                                   x_{24} <= 4
#                                   x_{3t} <= 3 
#                                   x_{4t} <= 2

import cplex

# Initialize
p = cplex.Cplex()
p.set_problem_type(cplex.Cplex.problem_type.LP)
p.objective.set_sense(p.objective.sense.maximize) # max problem

#       0     1     2     3     4     5     6
v   = ["s1", "13", "3t", "14", "s2", "24", "4t"] 
obj = [ 1. ,  0. ,  0. ,  0. ,  1. ,  0. ,  0. ]
lb  = [ 0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ]
ub  = [ 4. ,  2. ,  3. ,  1. ,  5. ,  4. ,  2. ] # Capacity constraints

p.variables.add(obj = obj, 
                lb = lb,
                ub = ub,
                names = v)
# Constraints
constraint_names = ["con1", "con2", "con3", "con4"]
                    #"cap1", "cap2", "cap3", "cap4", "cap5", "cap6", "cap7"]

# Conservation constraints
# xs1 - x12 - x14 = 0
con1 = [["s1", "13", "14"], [1., -1., -1.]]
# xs2 - x24 = 0
con2 = [["s2", "24"], [1., -1.]]
# x13 - x3t = 0
con3 = [["13", "3t"], [1., -1.]]
# x14 + x24 - x4t = 0
con4 = [["14", "24", "4t"], [1., 1., -1.]]
# Capacity constraints
#cap1 = [["s1"], [1.]] # <= 4
#cap2 = [["s2"], [1.]] # <= 5
#cap3 = [["13"], [1.]] # <= 2
#cap4 = [["14"], [1.]] # <= 1
#cap5 = [["24"], [1.]] # <= 4
#cap5 = [["3t"], [1.]] # <= 3
#cap6 = [["4t"], [1.]] # <= 2

constraints = [con1, con2, con3, con4]#,  # Conservation
               #cap1, cap2, cap3, cap4, cap5, cap6] # Capacity

rhs = [ 0, 0, 0, 0] 
        #4, 5, 2, 1, 4, 3, 2]
constraint_senses = [ "E", "E", "E", "E"]#, # Conservation
                      #"L", "L", "L", "L", "L", "L" ] # Capacity

p.linear_constraints.add(lin_expr = constraints,
                         senses = constraint_senses,
                         rhs = rhs,
                         names = constraint_names)

p.solve()
sol = (p.solution.get_values())
print("Solutions:")
print("s1, 13, 3t, 14, s2, 24, 4t")
print(sol)
print("Solutions:\
       \nx_s1 = {}\
       \nx_s2 = {}\
       \nx_13 = {}\
       \nx_3t = {}\
       \nx_14 = {}\
       \nx_24 = {}\
       \nx_4t = {}\
       ".format(sol[0], sol[4], sol[1], sol[2], sol[3], sol[5], sol[6]))
