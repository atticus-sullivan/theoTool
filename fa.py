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

import yaml
from ele import Ele
from pyformlang.finite_automaton import EpsilonNFA, State, Symbol, Epsilon
from terminaltables import SingleTable
import copy

def make_tuple(i:str):
    s = i.split(",")
    t = tuple(map(str, s))
    return t[0:3]

class AutomataRegul(Ele):
    def __init__(self, checks:list[str], aut:EpsilonNFA):
        super().__init__(terminals=list(map(lambda x: x.value, aut.symbols)), checks=checks)
        self.enfa   = aut
        self.states = aut.states

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
        return True

    def toDot(self,fi:str) -> bool:
        self.enfa.write_as_dot(fi)
        return True

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
    def loadYaml(cls, path:str, verbose:int):
        with open(path) as f:
            d = yaml.safe_load(f.read())

        enfa = EpsilonNFA()

        stateD  = {}
        symbolD = {}
        if 'delta' not in d or not isinstance(d['delta'], list):
            raise KeyError("delta key not defined in input or not a list")
        else:
            if verbose >= 1:
                print("delta transitions")
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
                if verbose >= 1:
                    print(*x)
            if verbose >= 1:
                print()

        if 'accepting' not in d or not isinstance(d['accepting'], list):
            raise KeyError("accepting key not defined in input")
        else:
            for a in d['accepting']:
                enfa.add_final_state(str(a))

        if 'initial' not in d:
            raise KeyError("initial key not defined in input")
        else:
            enfa.add_start_state(str(d['initial']))

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return AutomataRegul(aut=enfa, checks=d['check'])

        return AutomataRegul(aut=enfa, checks=[])

    def minimize(self):
        states = list(self.enfa.states)
        states.sort(key=lambda x : x.value)
        tab = [[None for _ in states] for _ in states]
        i = 0
        statesDict = {}
        for s in states:
            statesDict[states[i]] = i
            i += 1
        for s1 in range(len(states)):
            for s2 in range(len(states)):
                if s2 > s1: break # only handle lower left triangle
                if states[s1] not in self.enfa.final_states and states[s2] in self.enfa.final_states or states[s1] in self.enfa.final_states and states[s2] not in self.enfa.final_states:
                    tab[s1][s2] = "ε"
                    tab[s2][s1] = "ε"

        changed = True
        self.mini_tabToString(tab[:], states, False, "Step")
        print()
        while changed:
            changed = False
            for s1 in range(len(states)):
                for s2 in range(len(states)):
                    if s2 > s1: break # only handle lower left triangle
                    if tab[s1][s2] is not None: continue # difference is already descided

                    for w in sorted(self.terminals):
                        s1D = self.enfa._get_next_states_iterable([states[s1]], w)
                        s2D = self.enfa._get_next_states_iterable([states[s2]], w)
                        if len(s1D) != 1 or len(s2D) != 1:
                            print(s1D, s2D, w)
                            raise Exception("FA is not DFA -> no minimization")
                        s1D = s1D.pop()
                        s2D = s2D.pop()
                        if tab[statesDict[s1D]][statesDict[s2D]] is not None:
                            if tab[statesDict[s1D]][statesDict[s2D]] == "ε":
                                suff = w
                            else:
                                suff = w + tab[statesDict[s1D]][statesDict[s2D]]
                            if tab[s1][s2] is None or len(suff) < len(tab[s1][s2]):
                                print("Found (%s,%s) -%s> (%s,%s) to be different" % (states[s1],states[s2], w, s1D,s2D))
                                tab[s1][s2] = suff
                                tab[s2][s1] = suff
                                changed = True
            self.mini_tabToString(tab[:], states, False, "Step")
            print()

        self.mini_tabToString(tab[:], states, True, "Final")
    
    def mini_tabToString(self, tab, states, final, title):
        tab = copy.deepcopy(tab)
        for l,_ in enumerate(tab):
            for c,_ in enumerate(tab[l]):
                if c > l:
                    tab[l][c] = ""
                elif c == l:
                    tab[l][c] = states[c]
                elif tab[l][c] is None and final:
                    tab[l][c] = "="

        st = SingleTable(tab, title=title)
        for i in range(len(tab[-1])):
            st.justify_columns[i] = 'center'
        st.inner_row_border=True
        st.inner_heading_row_border=False
        print(st.table)

if __name__ == '__main__':
    fa = AutomataRegul.loadYaml("projects/miniTesting/klausur2020.yaml", 0)
    fa.minimize()
