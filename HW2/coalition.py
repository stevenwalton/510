import sys # For argv
import getopt # For options
import re # regex replacing
from functools import lru_cache # fast memoizing
import numpy as np
from itertools import permutations # Gets permutations

MAX_CACHE = None

######### Example ###############
#   4           Number of players
#   {1},30      {players in coalition},reward
#   {2},40
#   {3},25
#   {4},45
#   {1,2},50
#   {1,3},60
#   {1,4},80
#   {2,3},55
#   {2,4},70
#   {3,4},80
#   {1,2,3},90
#   {1,2,4},120
#   {1,3,4},100
#   {2,3,4},115
#   {1,2,3,4},140
#################################

class Coalition:
    strcuture = {}
    def __init__(self,coalition,numplayers):
        self.input_coalition = coalition
        self.numplayers = numplayers

    def permutes(self,key):
        return [''.join(i) for i in permutations(key)]


def readfile(filename:str, d:str=None,dtype_=str):
    r""" numpy read file wrapper """
    return np.loadtxt(str(filename), delimiter=d, dtype=dtype_)

def print_usage():
    r""" Prints file usage """
    print("usage: coalition.py -i <input file> -o <output file>")
    print("-i, --input\t sets the input file")
    print("-o, --output\t sets the output file: defaults to optimalCS.csv")
    print("-d, --delimiter\t sets the delimiter for ALL files. Defaults to None")
    #print("-c, --max-cache\t sets the maximum caching size for memoization. Defaults is None")

def command_line_args(argv):
    r""" Handles the command line arguments """
    try:
        opts, args = getopt.getopt(argv,"hp:i:o:d:",["help","params","payoff",\
                "output","delimiter"])
    except getopt.GetoptError:
        print_usage()
        exit(1)
    d = None
    output = "optimalCS.csv"
    if "-d" or "--delimiter" in opt:
        for opt, arg in opts:
            if opt == '-d' or opt == '--delimiter':
                d = str(arg)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            exit(0)
        elif opt in ("-i", "--input"):
            in_file = readfile(str(arg),d)
        elif opt in ("-o", "--output"):
            output = str(arg)
        elif opt in ("-c", "--max-cache"):
            MAX_CACHE = int(arg)
    return in_file,output

def format_input(input_file):
    #r""" Returns arrays of the coalitions and rewards """
    r""" Returns dictionary of the coalitions and rewards """
    numplayers = np.int(input_file[0])
    coalitions = {}
    for i in range(1,len(input_file)):
        data = re.sub("{|}","",input_file[i]).rsplit(',',1)
        coalitions[re.sub(",","",data[0])] = np.float(data[1])
    #coalitions = np.zeros((len(input_file)-1,numplayers))
    #rewards    = np.zeros(len(input_file)-1)
    #for i in range(1,len(input_file)):
    #    data = np.asarray(re.sub("{|}", "", \
    #            input_file[i]).split(','),\
    #            dtype=np.float)
    #    coalitions[i-1] = np.hstack((data[:-1],\
    #            np.repeat(0,\
    #            np.shape(coalitions[i-1])[0] - np.shape(data[:-1])[0])))
    #    rewards[i-1] = np.asarray(data[-1],dtype=np.float)
    #return coalitions,rewards
    return numplayers,coalitions

#@lru_cache(maxsize=MAX_CACHE)
def opt_coalition(coalition,coalition_dict):
    r""" """
    return max(coalition,coalition_dict[coalition])

def find_opt():
    r""" """
    pass

def opt_find():
    pass
    

    

def main(argv):
    in_file,out_file = command_line_args(argv)
    n,c = format_input(in_file)
    C = Coalition(c,n)
    #find_opt(c)

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print_usage()
        exit(1)
    main(sys.argv[1:])
