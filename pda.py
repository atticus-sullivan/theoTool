from pyformlang.pda import PDA, State, StackSymbol, Symbol, Epsilon
from ele import Ele
import yaml
from cfg import Cfg

def make_tuple(i:str):
    s = i.split(",")
    return tuple(s)

class Pda(Ele):
    
    def __init__(self, aut:PDA, checks:list[str]):
        super().__init__(terminals=list(map(lambda x: x.value, aut.input_symbols)), checks=checks)
        self.pda = aut
        self.states = aut.states
        self.cfg = None
        
    # returns (accepted,texTree,leftDeriv)
    # returns (accepted,[],[])
    def simulate(self, i:str):
        if self.cfg is None:
            self.cfg = Cfg(cfg=self.pda.to_cfg(),checks=self.checks)
        accepted = self.cfg.simulate(i)[0]
        r = ([],[])
        return accepted,r[0],r[1]

    def toTikz(self,f):
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

    def toDot(self, f):
        print("pda does no toDot()")

    @classmethod
    def load(cls, fi:str):
        with open(fi, 'r') as f:
            d = yaml.safe_load(f.read())

        pda = PDA()

        stateD = {}
        symbolD = {}
        sSymbolD = {}
        if 'delta' not in d or not isinstance(d['delta'], list):
            raise KeyError("delta key not defined in input (or not a list)")
        else:
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

                stackSymbs = list(map(lambda x: sSymbolD[x], t[4:]))
                x = (stateD[t[0]], symbolD[t[1]], sSymbolD[t[2]], stateD[t[3]], stackSymbs)
                pda.add_transition(*x)

        if 'startStack' not in d:
            raise KeyError("startStack key not defined in input")
        pda.set_start_stack_symbol(d['startStack'])

        if 'initial' not in d:
            raise KeyError("initial key not defined in input")
        pda.set_start_state(d['initial'])

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return Pda(aut=pda, checks=d['checks'])

        return Pda(aut=pda, checks=[])
