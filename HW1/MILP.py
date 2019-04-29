import numpy as np
import cplex
import sys
import getopt

def solve(targets,                  
          d_covered,                
          d_uncovered,              
          a_covered,                
          a_uncovered,              
          defender_resources:int=1, 
          attacker_resources:int=1, 
          ptype:str="MILP",         
          minimax:str="maximize"):  
    r""" 
    Solves a problem using CPlex. Currently only supports MILP

    [params]
    targets            : number of targets
    d_covered          : defender's payoff if target is covered
    d_uncovered        : defender's payoff if target is uncovered
    a_covered          : attacker's payoff if target is covered
    a_uncovered        : attacker's payoff if target is uncovered
    defender_resources : number of resources that defender has
    attacker_resources : number of resources that attacker has
    ptype              : type of problem: {MILP,LP,ILP,etc}
    minimax            : sets problem to maximization or minimization
    """
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
    v = ["z"+str(t) for t in range(num_targets)] + ["x"+str(t) for t in range(num_targets)]
    #obj = d_covered
    obj = d
    lb = np.zeros(len(obj))
    ub = np.ones(len(obj))
    # First two constraints will always be for the sums
    ub[0] = attacker_resources
    ub[1] = defender_resources

    p.variables.add(obj   = obj, # Objective function
                    lb    = lb,  # Lower bound
                    ub    = ub,  # Upper bound
                    names = v)   # Variable names
    # z_i \in {0,1} Set all z_i to integer values
    [p.variables.set_types([("z"+str(t),p.variables.type.integer)]) for t in range(num_targets)]
    # x_i \in [0,1] Set all x_i to continuous values
    [p.variables.set_types([("x"+str(t),p.variables.type.continuous)]) for t in range(num_targets)]

    constraints_names = []
    # sum z_i = 1
    con0 = ["z"+str(t) for t in range(num_targets)],[1.]*num_targets
    # sum x_i <= num_resources
    con1 = ["x"+str(t) for t in range(num_resources)],[1.]*num_targets

    # Constraints 3+
    for t in range(len(targets)):
        s = "con"+str(t+2)
        #s = str(t1) + "_" + str(t2)
        constraints_names.append(s)
        d - ()
        constraint = [[],[]]
        rhs = []
        constraint_senses = []

    constraint_senses = [""] * len(constraints_names)
    rhs = [0]*len(constraints_names)
    rhs[0] = attacker_resources # Attacker only has one resource
    rhs[1] = defender_resources # 2
    constraint_senses[0] = "E"
    constraint_senses[1] = "L"

    #constraints_names = ["con1"]
    #con1 = [[],[]]

    #constraints = [con1]
    #rho = []
    #constraint_senses = []

    p.linear_constraints.add(lin_expr = constraints,
                             senses   = constraints_names,
                             rhs      = rhs,
                             names    = constraint_names)

    p.solve()
    return p.solution.get_values()

def print_solution():
    r""" Function to print solution to std out """
    pass

def write_solution(solution, output_file):
    r""" Function to write solution to file """
    pass


def readfile(filename:str, d:str=','):
    r""" numpy read file wrapper """
    return np.loadtxt(str(filename), delimiter=d)

def print_usage():
    r""" Prints file usage """
    print("usage: MILP.py -p <parameter file> -i <payoff file> -o <output file>")
    print("-p, --params\t sets the parameter file")
    print("-i, --payoff\t sets the payoff file")
    print("-o, --output\t sets the output file")
    print("-d, --delimiter\t sets the delimiter of ALL files")

def command_line_args(argv):
    r""" Handles the command line arguments """
    try:
        opts, args = getopt.getopt(argv,"hp:i:o:d:",["help","params","payoff","output","delimiter"])
    except getopt.GetoptError:
        print_usage()
        exit(1)
    d = ','
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
    return parameters,payoff,output



def main(argv):
    params, payoff, output = command_line_args(argv)
    num_targets   = params[0]
    num_resources = params[1]
    def_cov       = payoff[:][1]
    def_uncov     = payoff[:][2]
    att_uncov     = payoff[:][3]
    att_cov       = payoff[:][4]
    del params
    del payoff

if __name__ == '__main__':
    if len(sys.argv) <= 4:
        print_usage()
        exit(1)
    main(sys.argv[1:])
