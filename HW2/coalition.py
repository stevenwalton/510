import sys # For argv
import getopt # For options
import re # regex replacing
import numpy as np
from itertools import permutations
from itertools import combinations

class Coalition:
    def __init__(self,coalition,numplayers):
        self.input_coalitions = coalition
        self.numplayers = numplayers
        self.best_structure = {}
        self.key_value = {}
        self.best_val = 0
        self.best_coalition = ""

    def permutes(self,key):
        unformatted_combos = []
        for i in range(1,len(key)//2 + 1):
            unformatted_combos += list(combinations(key,i))
        combos = [""]*len(unformatted_combos)
        for i in range(len(unformatted_combos)):
            combos[i] = "".join(unformatted_combos[i][:])
        combos = [combos[i] + "," for i in range(len(combos))]
        for i in range(len(combos)):
            for j in range(len(key)):
                if key[j] not in combos[i]:
                    combos[i] += key[j]
        # Only do assert from here because we have some redundancies in the small
        # keys. 
        # Commenting out checks because you might run different code
        #if key == "123":
        #    assert(combos==['1,23','2,13','3,12'])
        #elif key == '124':
        #    assert(combos==['1,24','2,14','4,12'])
        #elif key == '134':
        #    assert(combos==['1,34','3,14','4,13'])
        #elif key == '234':
        #    assert(combos==['2,34','3,24','4,23'])
        #elif key == "1234":
        #    # up to -1 because our method gives a '34,12' which is redundant
        #    assert(combos[:-1]==['1,234','2,134','3,124','4,123','12,34','13,24','14,23','23,14','24,13'])
        return combos
    # Originally did this to check the answer. Then checked above version with
    # these keys. They appear to match
        #if key == "12":
        #    return ["1,2"]
        #elif key == '13':
        #    return ['1,3']
        #elif key == '14':
        #    return ['1,4']
        #elif key == '23':
        #    return ['2,3']
        #elif key == '24':
        #    return ['2,4']
        #elif key == '34':
        #    return ['3,4']
        #elif key == "123":
        #    return ['1,23','2,13','3,12']
        #elif key == '124':
        #    return ['1,24','2,14','4,12']
        #elif key == '134':
        #    return ['1,34','3,14','4,13']
        #elif key == '234':
        #    return ['2,34','3,24','4,23']
        #elif key == "1234":
        #    return ['1,234','2,134','3,124','4,123','12,34','13,24','14,23','23,14','24,13']

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
            #self.key_value[key] = max(self.input_coalitions[key],max([self.get_value(k) for k in self.permutes(key)]))
            self.best_structure[key] = key
            self.key_value[key] = self.input_coalitions[key]
            permutes = self.permutes(key)
            for k in permutes:
                if self.get_value(k) > self.key_value[key]:
                    self.key_value[key] = self.get_value(k)
                    self.best_structure[key] = k

            if self.key_value[key] > self.best_val:
                self.best_val = self.key_value[key]

    def get_optimal(self):
        for key in self.input_coalitions:
            if len(key) == 1:
                self.key_value[key] = self.input_coalitions[key]
                self.best_structure[key] = key
            else:
                self.optimal_val(key)
        #print(self.best_val)
        self.best_coalition = self.get_best_coalition(key)
        #print(self.best_coalition)

    def get_best_coalition(self,key):
        keys = self.best_structure[key].split(',')
        return ','.join((self.best_structure[k] for k in keys))

    def print_to_file(self,output):
        s = '{{' + self.best_coalition.replace(',','},{') + "}}"
        s += "," + str(self.best_val) + "\n"
        with open(output,'w') as _file:
            _file.write(s)
        _file.close()

def readfile(filename:str, d:str=None,dtype_=str):
    r""" numpy read file wrapper """
    return np.loadtxt(str(filename), delimiter=d, dtype=dtype_)

def print_usage():
    r""" Prints file usage """
    print("usage: coalition.py -i <input file> -o <output file>")
    print("-h, --help\t prints this message")
    print("-i, --input\t sets the input file")
    print("-o, --output\t sets the output file: defaults to optimalCS.txt")

def command_line_args(argv):
    r""" Handles the command line arguments """
    try:
        opts, args = getopt.getopt(argv,"h:i:o:d:",["help","input=",\
                "output=","delimiter="])
    except getopt.GetoptError:
        print_usage()
        exit(1)
    output = "optimalCS.txt"
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            exit(0)
        elif opt in ("-i", "--input"):
            in_file = readfile(str(arg))
        elif opt in ("-o", "--output"):
            output = str(arg)
    return in_file,output

def format_input(input_file):
    #r""" Returns arrays of the coalitions and rewards """
    r""" Returns dictionary of the coalitions and rewards """
    numplayers = np.int(input_file[0])
    coalitions = {}
    for i in range(1,len(input_file)):
        data = re.sub("{|}","",input_file[i]).rsplit(',',1)
        coalitions[re.sub(",","",data[0])] = np.float(data[1])
    return numplayers,coalitions

def main(argv):
    in_file,out_file = command_line_args(argv)
    n,c = format_input(in_file)
    C = Coalition(c,n)
    C.get_optimal()
    C.print_to_file(out_file)

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print_usage()
        exit(1)
    main(sys.argv[1:])
