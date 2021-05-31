#!/bin/python3
import yaml
from typing import Callable
import argparse
import random
from AutomataExcept import AutomataKey, AutomataSuper
import sys
from ast import literal_eval as make_tuple
import itertools

# checks if word is in L #TODO define L here
def checkL(i:str):
    import re
    return len(re.findall("ab", i)) == len(re.findall('ba', i))

class AutomataRegul:
    def __init__(self, init:int, acc:list[int], states:list[int], sigma:list[str], checks:list[str]):
        self.init = init
        self.acc = acc
        self.states = states
        self.sigma = sigma
        self.checks = checks

    def simulate(self,i:str):
        raise AutomataSuper("simulate shouldn't be called on the AutomataRegul superclass")

    def checkRandom(self, startLen:int, endLen:int, cntPerLength:Callable[[int],int], checkL:Callable[[str],bool], check:bool):
        bs = []                              # store how many times the random word was in L and how often not
        for l in range(startLen, endLen):    # list of words of which length should be tested
            for _ in range(cntPerLength(l)): # how many words for each length should be tested
                string = ""                  # accumulator for word generation
                for _ in range(l):           # generate word
                    string += random.choice(self.sigma)

                if check:
                    b = checkL(string)           # check if word is in L
                    bs.append(b)
                    simRes = self.simulate(string)
                    if b != simRes[0]: # check if automata says the same
                        # if results differ, exit and print the word which failed
                        print("Wrong: ", simRes[0], simRes[1], string)
                        quit(1)
                else:
                    simRes = self.simulate(string)
                    bs.append(simRes[0])
                    print(simRes[0], string, simRes[1])

        print("True", len(list(filter(lambda x: x==True, bs))))
        print("False", len(list(filter(lambda x: x==False, bs))))

    def checkFixed(self, checkL:Callable[[str],bool], check:bool):
        checks = self.checks
        if checks == []:
            c = None
            while c != "":
                c = input("Input word to check")
                if not isinstance(c,str):
                    print("Error, no string input")
                else:
                    checks.append(c)
        bs = []                                    # store how many times the word was in L and how often not
        for string in checks:
            if check:
                b = checkL(string)                     # check if word is in L
                bs.append(b)
                simRes = self.simulate(string)
                print(string, simRes[0], simRes[1])
                if b != simRes[0]: # check if automata says the same
                    # if results differ, exit and print the word which failed
                    quit(1)
            else:
                simRes = self.simulate(string)
                bs.append(simRes[0])
                print(string, simRes[0], simRes[1])

        print()
        print("True", len(list(filter(lambda x: x==True, bs))))
        print("False", len(list(filter(lambda x: x==False, bs))))

    # doesn't load delta, returns yamlDict,objectDict
    @classmethod
    def load(cls, path:str):
        with open(path) as f:
            d = yaml.safe_load(f.read())

        if 'sigma' not in d or not isinstance(d['sigma'],list):
            raise AutomataKey("sigma key not defined in input or no list given")
        else:
            for c in d['sigma']:
                if not isinstance(c,str) or len(c) > 1:
                    raise AutomataKey("sigma element had more than 1 character or was no string/char")
            sigma = d['sigma']

        if 'states' not in d or not isinstance(d['states'], list):
            raise AutomataKey("states key not defined in input or no list given")
        else:
            for s in d['states']:
                if not isinstance(s, int) or s == -1:
                    raise AutomataKey("state wasn't an integer or state was '-1' which isn't allowed")
            states = d['states']

        if 'accepting' not in d or not isinstance(d['accepting'], list):
            raise AutomataKey("accepting key not defined in input")
        else:
            for a in d['states']:
                if not isinstance(a, int) or a not in states:
                    raise AutomataKey("accepting state was not a previously given state or no integer")
            acc = d['accepting']

        if 'initial' not in d or not isinstance(d['initial'], int):
            raise AutomataKey("initial key not defined in input")
        else:
            if d['initial'] not in states:
                raise AutomataKey("initial state is not in states")
            init = d['initial']

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(d["check"], str):
                    raise AutomataKey("element in check was not a string")
            return (d,{'sigma':sigma, 'states':states, 'acc':acc, 'init':init, 'checks':d['check']})

        return (d,{'sigma':sigma, 'states':states, 'acc':acc, 'init':init, 'checks':[]})

class DFA(AutomataRegul):
    def __init__(self, delta:Callable[[int,str],int], init:int, acc:list[int], states:list[int], sigma:list[str], checks:list[str]):
        super().__init__(init,acc,states,sigma,checks)
        self.delta = delta

    def simulate(self, i:str):
        path = [self.init]
        state = self.init
        for c in i:
            state = self.delta(state,c)
            path.append(state)

        if state in self.acc:
            return (True,path)
        else:
            return (False,path)

    # generate tikz code
    def toTikz(self, f):
        # preamble
        print(r"\documentclass{standalone}", file=f)
        print(r"\usepackage{tikz}", file=f)
        print(r"\usetikzlibrary{calc,positioning,fit,automata,arrows.meta,shapes.geometric}  % calc for $...$ calculations, positioning for .west .south positioning", file=f)
        print(r"\tikzset{" + "\n" + r"automata/.style={" + "\n" + r"every loop/.style={looseness=5},", file=f)
        print(r"every state/.style={very thick, fill=blue!20, draw=blue!50, text==black, ellipse},", file=f)
        print("->,>=Stealth[round], shorten >=1pt, auto, semithick,", file=f)
        print("node distance=2.8cm and 2.8cm," + "\n" + r"font=\small," + "\n" + r"initial text=,}}" + "\n", file=f)
        print(r"\begin{document}" + "\n" + r"\begin{tikzpicture}", file=f)
        # states
        for st in self.states:
            accepting = ",accepting" if st in self.acc else ""
            initial = ",initial" if st == self.init else ""
            print(r"\node[state%s%s] (%s) {%s};" % (accepting,initial,st,st),file=f)
        print("%",file=f)
        # transitions
        for st in self.states:
            for c in self.sigma:
                src = st
                dst = self.delta(st, c)
                if src == dst:
                    print(r"\path (%s) edge[loop above] node[] {%s} (%s);" % (src,c,dst), file=f)
                else:
                    print(r"\path (%s) edge[] node[] {%s} (%s);" % (src,c,dst), file=f)
        print(r"\end{tikzpicture}" + "\n" + r"\end{document}", file=f)

    @classmethod
    def load(cls, path:str):
        d,r = super().load(path)

        ret = {}
        if 'delta' not in d:
            raise AutomataKey("delta key not defined in input")
        else:
            todo = list(itertools.product(r['states'], r['sigma']))
            for k in d['delta'].keys():
                t = make_tuple(k)
                if not isinstance(t[0], int) or not isinstance(t[1], str) or len(t[1]) > 1:
                    raise AutomataKey("input tuples of delta have to be (int,char)")
                if t not in todo:
                    raise AutomataKey("delta is not deterministic")
                todo.remove(t)
                ret[t] = d['delta'][k]

            if todo != []:
                # TODO define unknown transitions to an error state
                raise AutomataKey("delta is not total")

        r['delta'] = lambda x,c: ret[(x,c)]
        return DFA(**r)
        # return AutomataRegul(delta=lambda x,c: ret[(x,c)], sigma=sigma, states=states, acc=acc, init=init, checks=[])

class NFA(AutomataRegul):
    def __init__(self, delta:Callable[[int,str],list[int]], init:int, acc:list[int], states:list[int], sigma:list[str], checks:list[str]):
        super().__init__(init,acc,states,sigma,checks)
        self.delta = delta

    def simulate(self,i:str):
        state = set([self.init])
        for c in i:
            state = set(map(lambda s: self.delta(s,c), state))

        if any([(s in self.acc) for s in state]):
            return (True,[])
        else:
            return (False,[])

    # generate tikz code
    def toTikz(self,f):
        # preamble
        print(r"\documentclass{standalone}", file=f)
        print(r"\usepackage{tikz}", file=f)
        print(r"\usetikzlibrary{calc,positioning,fit,automata,arrows.meta,shapes.geometric}  % calc for $...$ calculations, positioning for .west .south positioning", file=f)
        print(r"\tikzset{" + "\n" + r"automata/.style={" + "\n" + r"every loop/.style={looseness=5},", file=f)
        print(r"every state/.style={very thick, fill=blue!20, draw=blue!50, text==black, ellipse},", file=f)
        print("->,>=Stealth[round], shorten >=1pt, auto, semithick,", file=f)
        print("node distance=2.8cm and 2.8cm," + "\n" + r"font=\small," + "\n" + r"initial text=,}}" + "\n", file=f)
        print(r"\begin{document}" + "\n" + r"\begin{tikzpicture}", file=f)
        # states
        for st in self.states:
            accepting = ",accepting" if st in self.acc else ""
            initial = ",initial" if st == self.init else ""
            print(r"\node[state%s%s] (%s) {%s};" % (accepting,initial,st,st),file=f)
        print("%",file=f)
        # transitions
        for st in self.states:
            for c in self.sigma:
                src = st
                for dst in self.delta(st, c):
                    if src == dst:
                        print(r"\path (%s) edge[loop above] node[] {%s} (%s);" % (src,c,dst), file=f)
                    else:
                        print(r"\path (%s) edge[] node[] {%s} (%s);" % (src,c,dst), file=f)
        print(r"\end{tikzpicture}" + "\n" + r"\end{document}", file=f)

    #FIXME here transitions for the whole alphabet have to be defined
    @classmethod
    def load(cls, path:str):
        d,r = super().load(path)

        ret = {}
        if 'delta' not in d:
            raise AutomataKey("delta key not defined in input")
        else:
            for k in d['delta'].keys():
                t = make_tuple(k)
                if not isinstance(t[0], int) or not isinstance(t[1], str) or len(t[1]) > 1:
                    raise AutomataKey("input tuples of delta have to be (int,char)")
                if t not in ret:
                    ret[t] = [d['delta'][k]]
                ret[t].append([d['delta'][k]])

        r['delta'] = lambda x,c: ret[(x,c)]
        return NFA(**r)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("automataFile", help="YAML file specifying the automata, see README.md for required/optional values")
    parser.add_argument("tikzCodeOut", help="file to output the tex code, '-' for stdout, '+' for stderr")
    parser.add_argument("--startLen", "-s", help="Minimum length of the words to check", nargs=1, type=int)
    parser.add_argument("--endLen", "-e", help="Maximum length of the words to check", nargs=1, type=int)
    parser.add_argument("--check", "-c", help="Check input words via the 'checkL' function", action='store_true')

    args = parser.parse_args()

    automata = DFA.load(args.automataFile)
    if automata.checks != []:
        automata.checkFixed(checkL=checkL, check=args.check)
    else:
        automata.checkRandom(startLen=args.startLen[0], endLen=args.endLen[0], cntPerLength=lambda l: l, checkL=checkL, check=args.check)

    if args.tikzCodeOut == "-":
        f = sys.stdout
    elif args.tikzCodeOut == "+":
        f = sys.stderr
    else:
        f = open(args.tikzCodeOut, "w")
    automata.toTikz(f=f)
    f.close()


# TODO toDot for syntaxTrees
