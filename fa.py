import yaml
from ele import Ele
from pyformlang.finite_automaton import EpsilonNFA, State, Symbol, Epsilon

def make_tuple(i:str):
    s = i.split(",")
    return s[0:3]

class AutomataRegul(Ele):
    def __init__(self, checks:list[str], aut:EpsilonNFA):
        super().__init__(terminals=list(map(lambda x: x.value, aut.symbols)), checks=checks)
        self.enfa   = aut
        self.states = aut.states

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
            accepting = ",accepting" if self.enfa.is_final_state(st) else ""
            initial = ",initial" if st in self.enfa._start_state else ""
            print(r"\node[state%s%s] (%s) {%s};" % (accepting,initial,st.value,st.value),file=f)
        print("%",file=f)
        # transitions
        for st in self.states:
            for c in self.terminals:
                src = st.value
                for dst in self.enfa._get_next_states_iterable(current_states=[st], symbol=c):
                    dst = dst.value
                    if src == dst:
                        print(r"\path (%s) edge[loop above] node[] {%s} (%s);" % (src,c,dst), file=f)
                    else:
                        print(r"\path (%s) edge[] node[] {%s} (%s);" % (src,c,dst), file=f)
        print(r"\end{tikzpicture}" + "\n" + r"\end{document}", file=f)

    def toDot(self,f):
        self.enfa.write_as_dot(f)

    def toRegex(self):
        return self.enfa.to_regex()

    # returns (accepted,[],[])
    def simulate(self, i:str):
        l = [c for c in i]
        return(self.enfa.accepts(l),[],[])

    @classmethod
    def loadJflap(cls, path:str):
        path
        print("Error: loadJflap not implemented")

    @classmethod
    def loadYaml(cls, path:str):
        with open(path) as f:
            d = yaml.safe_load(f.read())

        enfa = EpsilonNFA()

        stateD  = {}
        symbolD = {}
        if 'delta' not in d or not isinstance(d['delta'], list):
            raise KeyError("delta key not defined in input")
        else:
            for d1 in d['delta']:
                t = make_tuple(d1)
                if t[0] not in stateD:
                    stateD[t[0]] = State(t[0])
                if t[2] not in stateD:
                    stateD[t[2]] = State(t[2])
                if t[1] not in symbolD:
                    if t[1] == "":
                        symbolD[t[1]] = Epsilon()
                    else:
                        symbolD[t[1]] = Symbol(t[1])

                x = (stateD[t[0]], symbolD[t[1]], stateD[t[2]])
                enfa.add_transition(*x)

        if 'accepting' not in d or not isinstance(d['accepting'], list):
            raise KeyError("accepting key not defined in input")
        else:
            for a in d['accepting']:
                enfa.add_final_state(str(a))

        if 'initial' not in d or not isinstance(d['initial'], int):
            raise KeyError("initial key not defined in input")
        else:
            enfa.add_start_state(str(d['initial']))

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return AutomataRegul(aut=enfa, checks=d['checks'])

        return AutomataRegul(aut=enfa, checks=[])
