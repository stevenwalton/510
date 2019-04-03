# Tutorial from 
# https://www-01.ibm.com/support/docview.wss?uid=swg27042869&aid=1
import cplex
import sys

def sample1(filename):
    c = cplex.Cplex(filename)

    try:
        c.solve()
    except CplexSolverError:
        print("Exception raised during solve")
        return
    # solution.get_status() returns an integer code
    status = c.solution.get_status()
    print("Solution status = {} : {}").format(status,c.solution.status[status])
    print("Objective value = {}").format(c.solution.get_objective_value())

if __name__ == '__main__':
    sample1("lpex1.lp")
