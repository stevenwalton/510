import numpy as np
import cplex
import sys
import getopt

def solve(targets,                  
          payoff,
          defender_resources:int=1, 
          attacker_resources:int=1, 
          ptype:str="MILP",         
          minimax:str="maximize"):  
    r""" 
    Solves a problem using CPlex. Currently only supports MILP

    [params]
    targets            : number of targets
    defender_resources : number of resources that defender has
    attacker_resources : number of resources that attacker has
    ptype              : type of problem: {MILP,LP,ILP,etc}
    minimax            : sets problem to maximization or minimization
    """
    # Need a big number. Will lower bound later
    M = 9999

    p = cplex.Cplex()
    if ptype in ("milp", "MILP"):
        p.set_problem_type(cplex.Cplex.problem_type.MILP)
    else:
        print("Problem type:",ptype,"is not currently supported")
        exit(1)

    if minimax in ("max","maximize"):
        p.objective.set_sense(p.objective.sense.maximize)
    elif minimax in ("min","minimize"):
        p.objective.set_sense(p.objective.sense.minimize)
    else:
        print("Only solves maximization or minimization problems")

    num_targets = len(targets)
    # v is the z's, x's, v_def, and v_att
    v = ["z"+str(t) for t in range(num_targets)] \
        + ["x"+str(t) for t in range(num_targets)] \
        + ["v_def","v_att"]                             
    num_variables = len(v)
    obj = np.zeros(num_variables)
    for i in range(num_variables):
        if v[i] == "v_def":
            obj[i] = 1.
    lb = np.zeros(num_variables)
    ub = np.ones(num_variables)
    for i in range(num_variables):
        if v[i] in ("v_def","v_att"):
            ub[i] = cplex.infinity
            lb[i] = -1*cplex.infinity

    p.variables.add(obj   = obj, # Objective function
                    lb    = lb,  # Lower bound
                    ub    = ub,  # Upper bound
                    names = v)   # Variable names
    # z_i \in {0,1} Set all z_i to integer values
    [p.variables.set_types([("z"+str(t),p.variables.type.integer)]) for t in range(num_targets)]
    # x_i \in [0,1] Set all x_i to continuous values
    [p.variables.set_types([("x"+str(t),p.variables.type.continuous)]) for t in range(num_targets)]
    # Also set for attacker and defender
    p.variables.set_types([("v_def",p.variables.type.continuous)])
    p.variables.set_types([("v_att",p.variables.type.continuous)])

    util_du = [M+payoff[i][2] for i in range(num_targets)]
    util_dc = [payoff[i][3] for i in range(num_targets)]
    util_ac = [M+payoff[i][3] for i in range(num_targets)]
    init_params = np.array([1.,defender_resources])
    rhs = np.hstack((init_params, util_du, util_dc, util_ac))

    senses = ["E","L"] \
           + ["L" for i in range(num_targets)] \
           + ["G" for i in range(num_targets)]\
           + ["L" for i in range(num_targets)]
    

    constraints = []
    zl = []
    zc = []
    xl = []
    xc = []
    for t in range(num_targets):
        zl.append("z"+str(t))
        zc.append(1.)
        xl.append("x"+str(t))
        xc.append(1.)
    constraints.append([zl,zc])
    constraints.append([xl,xc])

    # Defender's utility
    # Interleave vars and coefficients
    # Easier doing it this way that inline loops
    def_util_vars = []#np.zeros(num_targets*3)
    def_util_coef = []#np.zeros(num_targets*3)
    def_util = []
    for i in range(num_targets):
        def_util_vars = (["v_def", "x"+str(i), "z"+str(i)])
        def_util_coef = ([1., (payoff[i][2] - payoff[i][1]), M])
        constraints.append([def_util_vars, def_util_coef])



    # Attacker strats
    att_strat_vars = []
    att_strat_coef = []
    att_strat = []
    for i in range(num_targets):
        att_strat_vars = (["v_att", "x"+str(i)])
        att_strat_coef = ([1., payoff[i][3] - payoff[i][4]])
        constraints.append([att_strat_vars,att_strat_coef])


    # Attacker utility
    att_util_vars = []
    att_util_coef = []
    att_util = []
    for i in range(num_targets):
        att_util_vars = (["v_att", "x"+str(i), "z"+str(i)])
        att_util_coef = ([1., payoff[i][3] - payoff[i][4], M])
        constraints.append([att_util_vars, att_util_coef])

    # Throw them all together
    constraint_names = ["r"+str(i) for i in range(len(constraints))]

    p.linear_constraints.add(lin_expr = constraints,
                             senses   = senses,
                             rhs      = rhs,
                             names    = constraint_names)
    p.solve()
    return p.solution.get_values()

def print_solution():
    r""" Function to print solution to std out """
    pass

def write_solution(n,solution, output_file="out.csv", delimiter=','):
    r""" Function to write solution to file """
    to_print = solution[int(n):-2]
    with open(output_file,'w') as _file:
        for i in range(len(to_print)):
            s = str(i+1) + delimiter + str(to_print[i]) + str("\n")
            _file.write(s)
    _file.close()

def readfile(filename:str, d:str=','):
    r""" numpy read file wrapper """
    return np.loadtxt(str(filename), delimiter=d)

def print_usage():
    r""" Prints file usage """
    print("usage: MILP.py -p <parameter file> -i <payoff file> -o <output file>")
    print("-p, --params\t sets the parameter file")
    print("-i, --payoff\t sets the payoff file")
    print("-o, --output\t sets the output file. Defaults to out.csv")
    print("-d, --delimiter\t sets the delimiter of ALL files. Defaults to csv")

def command_line_args(argv):
    r""" Handles the command line arguments """
    try:
        opts, args = getopt.getopt(argv,"hp:i:o:d:",["help","params","payoff","output","delimiter"])
    except getopt.GetoptError:
        print_usage()
        exit(1)
    d = ','
    output = "out.csv"
    if "-d" or "--delimiter" in opt:
        for opt, arg in opts:
            if opt == '-d' or opt == '--delimiter':
                d = str(arg)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            exit(0)
        elif opt in ("-p", "--params"):
            parameters = readfile(str(arg),d)
        elif opt in ("-i", "--payoff"):
            payoff = readfile(str(arg),d)
        elif opt in ("-o", "--output"):
            output = str(arg)
    return parameters,payoff,output,d



def main(argv):
    params, payoff, output, d = command_line_args(argv)
    num_targets   = params[0]
    num_resources = params[1]
    targets       = payoff[:,0]
    sol = solve(targets, payoff, num_resources)
    write_solution(num_targets,sol, output,d)


if __name__ == '__main__':
    if len(sys.argv) <= 4:
        print_usage()
        exit(1)
    main(sys.argv[1:])
