import numpy as np
import cplex
import sys
import getopt

def solve(targets,                  
          payoff,
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
    # Need a big number. Will lower bound later
    #M = 9999
    M=1000

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
    # First two constraints will always be for the sums
    #ub[0] = attacker_resources
    #ub[1] = defender_resources

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

    # RHS v_def is num_targets, v_att is 2x num_targets
    # Utility of defender when uncovered
    #util_du = M+d_uncovered
    #util_du = M+d_covered
    util_du = []
    util_dc = []
    util_ac = []
    for i in range(num_targets):
        util_du.append(M+payoff[i][2])
        util_dc.append(payoff[i][3])
        util_ac.append(M+payoff[i][3])
    # Utility of attacker uncovered: Already done
    # Utility of attacker when covered
    #util_ac = M+d_covered
    #print(util_du)
    #print(a_uncovered)
    #print(util_ac)
    #test = [1.] + [defender_resources]
    init_params = np.array([1.,defender_resources])
    #print(test)
    #print(np.hstack((test,util_du)))
    #print(util_du + a_uncovered + util_ac)
    #rhs = [1.,defender_resources] + util_du + a_uncovered + util_ac
    #rhs = np.hstack((init_params,util_du,d_uncovered,util_ac))
    rhs = np.hstack((init_params, util_du, util_dc, util_ac))
    #rhs = []
    #rhs.append(init_params)
    #rhs.append(util_du)
    #rhs.append(util_dc)
    #rhs.append(util_ac)
    #print("d_covered",d_covered)
    #print("d_uncovered", d_uncovered)
    #print("a_covered", a_covered)
    #print("a_uncovered", a_uncovered)

    #print(init_params) #good
    #print(util_du) # good
    #print(util_dc) # good
    #print(util_ac) # good
    #print(rhs)
    #print("=========")
    senses = ["E","L"] \
           + ["L" for i in range(num_targets)] \
           + ["G" for i in range(num_targets)]\
           + ["L" for i in range(num_targets)]
    
    #zs = np.vstack((["z"+str(t+1) for t in range(num_targets)],np.ones(num_targets)))
    #xs = np.vstack((["x"+str(t+1) for t in range(num_targets)],np.ones(num_targets)))

    #z_x = np.vstack((zs,xs))
        

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
    #def_util_vars = [["v_def","x"+str(t+1),"z"+str(t+1)] for t in range(num_targets)]
    #def_util_coef = [[1.,(d_uncovered[t] - d_covered[t])] for t in range(num_targets)] 
    # Interleave vars and coefficients
    #def_util = np.vstack((def_util_vars,def_util_coef)).reshape((-1,),order='F')
    def_util_vars = []#np.zeros(num_targets*3)
    def_util_coef = []#np.zeros(num_targets*3)
    def_util = []
    for i in range(num_targets):
        def_util_vars = (["v_def", "x"+str(i), "z"+str(i)])
        #def_util_coef = ([1., (d_uncovered[i] - d_covered[i]), M])
        def_util_coef = ([1., (payoff[i][2] - payoff[i][1]), M])
        #def_util.append([def_util_vars, def_util_coef])
        constraints.append([def_util_vars, def_util_coef])



    # Attacker strats
    #att_strat_vars = [["v_att", ("x"+str(t+i))] for t in range(num_targets)]
    #att_strat_coef = [[1.,(a_uncovered[t]-a_covered[t])] for t in range(num_targets)]
    #print(att_strat_vars)
    #print(att_strat_coef)
    #att_strat = np.vstack((att_strat_vars,att_strat_coef)).reshape((-1,),order='F')
    att_strat_vars = []#np.zeros(num_targets*3)
    att_strat_coef = []#np.zeros(num_targets*3)
    att_strat = []
    for i in range(num_targets):
        att_strat_vars = (["v_att", "x"+str(i)])
        #att_strat_coef = ([1., a_uncovered[i] - a_covered[i]])
        att_strat_coef = ([1., payoff[i][3] - payoff[i][4]])
        #att_strat.append([att_strat_vars,att_strat_coef])
        constraints.append([att_strat_vars,att_strat_coef])


    # Attacker utility
    #att_util_vars = [["v_att","x"+str(t+1),"z"+str(t+1)] for t in range(num_targets)]
    #att_util_coef = [[1.,(a_uncovered[t] - a_covered[t]),M] for t in range(num_targets)]
    #att_util = np.vstack((att_util_vars, att_util_coef)).reshape((-1,),order='F')
    att_util_vars = []
    att_util_coef = []
    att_util = []
    for i in range(num_targets):
        att_util_vars = (["v_att", "x"+str(i), "z"+str(i)])
        #att_util_coef = ([1., a_uncovered[i] - a_covered[i], M])
        att_util_coef = ([1., payoff[i][3] - payoff[i][4], M])
        #att_util.append([att_util_vars, att_util_coef])
        constraints.append([att_util_vars, att_util_coef])

    # Throw them all together
    #constraints = np.vstack((z_x, def_util, att_strat, att_util))
    constraint_names = ["r"+str(i) for i in range(len(constraints))]
    #print("constraint names\n",constraint_names)
    #print("constraints\n",constraints)
    #print("senses\n",senses)
    #print("rhs\n",rhs)

    p.linear_constraints.add(lin_expr = constraints,
                             senses   = senses,
                             rhs      = rhs,
                             names    = constraint_names)
    #p.linear_constraints.add(lin_expr = constraints)
    #p.linear_constraints.add(senses = senses)
    #p.linear_constraints.add(rhs = rhs)
    #p.linear_constraints.add(names=constraint_names)

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
    targets       = payoff[0][:]
    def_cov       = payoff[1][1:]
    def_uncov     = payoff[2][1:]
    att_uncov     = payoff[3][1:]
    att_cov       = payoff[4][1:]
    #del params
    #del payoff
    sol = solve(targets, payoff, def_cov, def_uncov, att_cov, att_uncov, num_resources)
    print(sol)


if __name__ == '__main__':
    if len(sys.argv) <= 4:
        print_usage()
        exit(1)
    main(sys.argv[1:])
