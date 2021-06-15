import yaml
from ele import Ele
from tmLib import NDTM

def make_tuple(i:str):
    s = i.split(",")
    t = tuple(map(str, s))
    return t

class Ndtm(Ele):
    def __init__(self, checks:list[str], aut:NDTM, terminals:list[str], states:list[str]):
        super().__init__(terminals=terminals, checks=checks)
        self.ndtm   = aut
        self.states = states

    def toTikz(self,f) -> bool:
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
            self.ndtm.start
            accepting = ",accepting" if st == self.ndtm.final else ""
            initial = ",initial" if st == self.ndtm.start else ""
            print(r"\node[state%s%s] (%s) {%s};" % (accepting,initial,st,st),file=f)
        print("%",file=f)
        # transitions
        for s,movements in self.ndtm.trans.items():
            print("s", s)
            src,read = s
            for dst,out in movements:
                for write,move in out:
                    c = (str(read[0])+"/"+str(write)+","+str(move)).replace("#", r"\#")
                    if src == dst:
                        print(r"\path[->] (%s) edge[loop above] node[] {%s} (%s);" % (src,c,dst), file=f)
                    else:
                        print(r"\path[->] (%s) edge[] node[] {%s} (%s);" % (src,c,dst), file=f)
        print(r"\end{tikzpicture}" + "\n" + r"\end{document}", file=f)
        return True

    def toDot(self,fi:str) -> bool:
        print("Ndtm does no toDot")
        return False

    # returns (accepted,[],[])
    def simulate(self, i:str):
        ret = self.ndtm.accepts(i)
        return (False if ret is None else True, ret, [])

    @classmethod
    def loadJflap(cls, path:str):
        path
        print("Error: loadJflap not implemented")

    @classmethod
    def loadYaml(cls, path:str, verbose:int):
        with open(path) as f:
            d = yaml.safe_load(f.read())

        if 'accepting' not in d:
            raise KeyError("accepting key not defined in input")
        else:
            final = d['accepting']

        if 'initial' not in d:
            raise KeyError("initial key not defined in input")
        else:
            init = str(d['initial'])

        if 'space' not in d:
            raise KeyError("space key not defined in input")
        else:
            space = str(d['space'])

        ndtm = NDTM(final=final, start=init, blank=space)

        if 'delta' not in d or not isinstance(d['delta'], list):
            raise KeyError("delta key not defined in input or not a list")
        else:
            if verbose >= 1:
                print("delta transitions")
            terminals = set()
            states    = set()
            for d1 in d['delta']:
                t = make_tuple(d1)
                # def addTrans(self, state, read_sym(potentially multiple ones), new_state, moves(symbol,direction)): 
                # yaml: state,read,write,state,move
                # tm.addTrans('q0', ('0', ), 'q0', (('1', 'R'), )) 
                x = (t[0], (t[1],), t[3], ((t[2],t[4]),))
                if (t[4] not in ['R','L','S']):
                    raise KeyError("Movement has to be either 'L'eft, 'R'ight or 'S'tay")
                states.add(t[0])
                states.add(t[3])
                terminals.add(t[1])
                terminals.add(t[2])
                ndtm.addTrans(*x)
                if verbose >= 1:
                    print(*x)
            if verbose >= 1:
                print()

            # remove space char from list of terminals
            terminals.remove(space)

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return Ndtm(aut=ndtm, checks=d['checks'], terminals=list(terminals), states=list(states))

        return Ndtm(aut=ndtm, checks=[], terminals=list(terminals), states=list(states))
