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
    best_strcuture = {}
    key_value = {}
    best_val = 0
    def __init__(self,coalition,numplayers):
        self.input_coalitions = coalition
        self.numplayers = numplayers

    def permutes(self,key):
        if key == "12":
            return ["1,2"]
        elif key == '13':
            return ['1,3']
        elif key == '14':
            return ['1,4']
        elif key == '23':
            return ['2,3']
        elif key == '24':
            return ['2,4']
        elif key == '34':
            return ['3,4']
        elif key == "123":
            return ['1,23','2,13','3,12']
        elif key == '124':
            return ['1,24','2,14','4,12']
        elif key == '134':
            return ['1,34','3,14','4,13']
        elif key == '234':
            return ['2,34','3,24','4,23']
        elif key == "1234":
            return ['1,234','2,134','3,124','4,123','12,23','13,24','14,23']

    def set_structure(self,key,val):
        n_key = sort(key)
        if n_key in best_strcuture:
            print("This key is already here")
            exit(1)
        self.best_structure[n_key] = key
        self.key_value[n_key] = val
        if self.best_val is None:
            self.best_val = val
        elif val > self.best_val:
            self.best_val = val

    def get_value(self,key):
        t = 0
        for k in key.split(','):
            #if k == ',': continue
            #if self.has_key(k): 
            if k in self.key_value:
                tt = self.key_value[k]
            else:
                t_key = [key[i] for i in k.split(',')]
                tt = max([max(t,t_key[i]) for i in range(len(tk))])
            t += tt
        return t

    def optimal_val(self,key):
        if key not in self.key_value:
            self.key_value[key] = max(self.input_coalitions[key],max([self.get_value(k) for k in self.permutes(key)]))
            if self.key_value[key] > self.best_val:
                self.best_val = self.key_value[key]

    def get_optimal(self):
        for key in self.input_coalitions:
            if len(key) == 1:
                self.key_value[key] = self.input_coalitions[key]
            else:
                self.optimal_val(key)
        print(self.best_val)


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

def opt_find():
    pass
    

    

def main(argv):
    in_file,out_file = command_line_args(argv)
    n,c = format_input(in_file)
    C = Coalition(c,n)
    C.get_optimal()

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print_usage()
        exit(1)
    main(sys.argv[1:])
