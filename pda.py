# Copyright (c) 2024 Lukas Heindl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pyformlang.pda import PDA, State, StackSymbol, Symbol, Epsilon
from ele import Ele
import yaml
from cfg import Cfg

def make_tuple(i:str):
    s = i.split(",")
    t = tuple(map(str, s))
    return t

class Pda(Ele):

    def __init__(self, aut:PDA, checks:list[str], acc:bool):
        super().__init__(terminals=list(map(lambda x: x.value, aut.input_symbols)), checks=checks)
        self.pda = aut
        self.states = aut.states
        self.cfg = None
        self.accepting = acc

    # returns (accepted,texTree,leftDeriv)
    # returns (accepted,[],[])
    def simulate(self, i:str):
        if self.cfg is None:
            if self.accepting:
                print("final -> empt Stack -> cfg")
                self.cfg = Cfg(cfg=self.pda.to_empty_stack().to_cfg(),checks=self.checks)
            else:
                print("empt Stack -> cfg")
                self.cfg = Cfg(cfg=self.pda.to_cfg(),checks=self.checks)
        accepted = self.cfg.simulate(i)[0]
        r = ([],[])
        return accepted,r[0],r[1]

    def toTikz(self,f) -> bool:
        # preamble
        print(r"\documentclass{standalone}", file=f)
        print(r"\usepackage{tikz}", file=f)
        print(r"\usetikzlibrary{calc,positioning,fit,automata,arrows.meta,shapes.geometric}  % calc for $...$ calculations, positioning for .west .south positioning", file=f)
        print(r"\tikzset{ownLoop/.style={->,shorten >=1pt,in=#1-15,out=#1+15,looseness=8}," + "\n" + r"automata/.style={" + "\n" + r"every loop/.style={looseness=5},", file=f)
        print(r"every state/.style={very thick, fill=blue!20, draw=blue!50, text==black, ellipse},", file=f)
        print("->,>=Stealth[round], shorten >=1pt, auto, semithick,", file=f)
        print("node distance=2.8cm and 2.8cm," + "\n" + r"font=\small," + "\n" + r"initial text=,}}" + "\n", file=f)
        print(r"\begin{document}" + "\n" + r"\begin{tikzpicture}", file=f)
        # states
        for st in self.states:
            initial = ",initial" if st == self.pda.start_state else ""
            print(r"\node[state%s] (%s) {%s};" % (initial,st.value,st.value),file=f)
        print("%",file=f)
        # transitions
        #self.pda.to_dict()) # can be used to collapes printed connections to: sameLeft side -> one connection
        for transition in self.pda._transition_function:
            src = transition[0][0].value
            dst = transition[1][0].value
            char = transition[0][1].value
            stackBefore = transition[0][2].value
            after = list(map(lambda x:x.value, transition[1][1:][0]))
            print(after)
            if after == ['']:
                stackAfter = "§"
            else:
                stackAfter = "".join(after)
            if src == dst:
                print(r"\path (%s) edge[ownLoop=90] node[] {%s} (%s); %% TODO set loop center position (degree) with the parameter of ownLoop" % (src,str(char)+","+str(stackBefore)+"/"+str(stackAfter),dst), file=f)
            else:
                print(r"\path (%s) edge[] node[] {%s} (%s);" % (src,str(char)+","+str(stackBefore)+"/"+str(stackAfter),dst), file=f)
        print(r"\end{tikzpicture}" + "\n" + r"\end{document}", file=f)
        return True

    def toDot(self, fi:str) -> bool:
        print("pda does no toDot()")
        return False

    @classmethod
    def loadYaml(cls, fi:str, verbose:int):
        with open(fi, 'r') as f:
            d = yaml.safe_load(f.read())

        pda = PDA()

        stateD = {}
        symbolD = {}
        sSymbolD = {}
        if 'delta' not in d or not isinstance(d['delta'], list):
            raise KeyError("delta key not defined in input (or not a list)")
        else:
            if verbose >= 1:
                print("Delta transitions")
            for d1 in d['delta']:
                t = make_tuple(d1)
                if t[0] not in stateD:
                    stateD[t[0]] = State(t[0])         # start state
                if t[1] not in symbolD:
                    if t[1] == "":
                        symbolD[t[1]] = Epsilon()
                    else:
                        symbolD[t[1]] = Symbol(t[1])   # read input symbol
                if t[2] not in sSymbolD:
                    sSymbolD[t[2]] = StackSymbol(t[2]) # top stack symbol
                if t[3] not in stateD:
                    stateD[t[3]] = State(t[3])         # destination state

                # rest are stacksymbols
                for stackSymb in t[4:]:
                    if stackSymb not in sSymbolD:
                        sSymbolD[t[4]] = StackSymbol(stackSymb) #TODO order

                stackSymbs = list(map(lambda x: sSymbolD[x], filter(lambda x: x != '', t[4:])))
                x = (stateD[t[0]], symbolD[t[1]], sSymbolD[t[2]], stateD[t[3]], stackSymbs)
                pda.add_transition(*x)
                if verbose >= 1:
                    print(*x)
            if verbose >= 1:
                print()

        if 'startStack' not in d:
            raise KeyError("startStack key not defined in input")
        pda.set_start_stack_symbol(str(d['startStack']))

        if 'initial' not in d:
            raise KeyError("initial key not defined in input")
        pda.set_start_state(str(d['initial']))

        accepting = False
        if 'accepting' in d:
            print("Note that acceptance on final state is not tested, yet")
            for a in d['accepting']:
                pda.add_final_state(str(a))
            accepting = True

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return Pda(aut=pda, checks=d['check'], acc=accepting)

        return Pda(aut=pda, checks=[], acc=accepting)
