import numpy as np
import cplex
import sys
import getopt

def solve(targets,                  
          payoff,
          defender_resources:int=1, 
          attacker_resources:int=1, 
          alpha=0,
          epsilon=0,
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

    if minimax in ("max","maximize"):
        p.objective.set_sense(p.objective.sense.maximize)
    elif minimax in ("min","minimize"):
        p.objective.set_sense(p.objective.sense.minimize)
    else:
        print("Only solves maximization or minimization problems")

    num_targets = len(targets)
    v = ["z"+str(t) for t in range(num_targets)] \
        + ["q"+str(t) for t in range(num_targets)] \
        + ["x"+str(t) for t in range(num_targets)] \
        + ["x'"+str(t) for t in range(num_targets)] \
        + ["v_def","v_att"]                             
    num_variables = len(v)
    obj = np.zeros(num_targets*4 + 2)
    for i in range(len(obj)):
        if v[i] == "v_def":
            obj[i] = 1.
    lb = np.zeros(num_variables)
    ub = np.ones(num_variables)
    for i in range(num_variables):
        if v[i] in ("v_def","v_att"):
            ub[i] = cplex.infinity
            lb[i] = -1*cplex.infinity

    ctypes = num_targets*'I'
    ctypes += num_targets*'I'
    ctypes += num_targets*'C'
    ctypes += num_targets*'C'
    ctypes += "CC"
    p.variables.add(obj   = obj,    # Objective function
                    lb    = lb,     # Lower bound
                    ub    = ub,     # Upper bound
                    names = v,      # Variable names
                    types = ctypes, # Types
                    )

    init_params = np.array([1.,1.,defender_resources])
    util_attUncov = [payoff[i][2] for i in range(num_targets)]
    util_attUncov2 = [payoff[i][2]+M for i in range(num_targets)]
    util_eopt = [payoff[i][2] + epsilon for i in range(num_targets)]
    util_eopt2 = [payoff[i][2] + epsilon + M for i in range(num_targets)]
    util_perceived = [alpha/num_targets +(0*i) for i in range(num_targets)]
    util_worst = [payoff[i][1] + M for i in range(num_targets)]

    rhs = np.hstack((init_params, util_attUncov,util_attUncov2, util_eopt, util_eopt2, util_perceived, util_worst))

    senses = ["E","G","L"] \
           + ["G" for i in range(num_targets)] \
           + ["L" for i in range(num_targets)] \
           + ["G" for i in range(num_targets)]\
           + ["L" for i in range(num_targets)]\
           + ["E" for i in range(num_targets)]\
           + ["L" for i in range(num_targets)]
    

    constraints = []
    zl = []
    zc = []
    xl = []
    xc = []
    ql = []
    qc = []
    for t in range(num_targets):
        zl.append("z"+str(t))
        zc.append(1.)
        xl.append("x"+str(t))
        xc.append(1.)
        ql.append("q"+str(t))
        qc.append(1.)

    constraints.append([zl,zc])
    constraints.append([ql,qc])
    constraints.append([xl,xc])

    # attacker optimal target
    v = []
    c = []
    for i in range(num_targets):
        v = ['v_att', "x'"+str(i)]
        c = [1., payoff[i][2] - payoff[i][3]]
        constraints.append([v,c])

    # attacker optimal target (M)
    for i in range(num_targets):
        v = ['v_att', "x'"+str(i), "z"+str(i)]
        c = [1., payoff[i][2] - payoff[i][3], M]
        constraints.append([v,c])

    for i in range(num_targets):
        v = ['v_att', "x'"+str(i), "q"+str(i)]
        c = [1., payoff[i][2] - payoff[i][3], epsilon]
        constraints.append([v,c])

    for i in range(num_targets):
        v = ['v_att', "x'"+str(i), "q"+str(i)]
        c = [1., payoff[i][2] - payoff[i][3], M]
        constraints.append([v,c])

    # perceived strat
    for i in range(num_targets):
        v = ["x'"+str(i), "x"+str(i)]
        c = [1., alpha-1]
        constraints.append([v,c])

    # Worst case
    for i in range(num_targets):
        v = ["v_def", "x"+str(i), "q"+str(i)]
        c = [1., payoff[i][1] - payoff[i][0], M]
        constraints.append([v,c])

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

def write_solution(offset:int,
                   num_targets:int,
                   solution, 
                   outfile:str="out.csv", 
                   delimiter:str=','):
    r""" Function to write solution to file """
    length = offset + num_targets
    it = 0
    with open(outfile,'w') as _file:
        for i in range(offset,length):
            it += 1
            s = str(it) + delimiter + str(solution[i]) + str("\n")
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
    num_targets   = int(params[0])
    num_resources = int(params[1])
    alpha         = params[2]
    epsilon       = params[3]
    targets       = payoff[:,0]
    payoff        = payoff[:,1:]
    sol = solve(targets, payoff, num_resources, alpha=alpha, epsilon=epsilon)
    print(sol)
    write_solution(offset=num_targets*num_resources,
                   num_targets=num_targets,
                   solution=sol, 
                   outfile=output,
                   delimiter=d)


if __name__ == '__main__':
    if len(sys.argv) <= 4:
        print_usage()
        exit(1)
    main(sys.argv[1:])
