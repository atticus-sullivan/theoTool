import yaml
from ele import Ele
from pyformlang.cfg import CFG, Terminal
from pyformlang.cfg.cyk_table import CYKTable, DerivationDoesNotExist
from pyformlang.cfg.parse_tree import ParseTree
from terminaltables import SingleTable

class Cfg(Ele):
    def __init__(self, cfg:CFG, checks:list[str]):
        super().__init__(terminals=list(map(lambda x: x.value, cfg.terminals)), checks=checks)
        self.cfg = cfg
        self.ts = []
        self.cyk_on_sim = False

    @classmethod
    def loadYaml(cls, fi:str, verbose:int):
        with open(fi, 'r') as f:
            i = yaml.safe_load(f.read())
            if 'prods' not in i or not isinstance(i['prods'], list):
                raise KeyError("a CFG needs a production key which has to contain a list of productions")
            prods = i['prods']
            cfg = CFG.from_text("\n".join(map(lambda x:str(x), prods)))

            if 'checks' in i:
                if not isinstance(i['checks'], list):
                    raise KeyError("checks has to contain a list")
                checks = list(map(lambda x: str(x), i['checks']))
            else:
                checks = []
            if verbose >= 1:
                print("Productions:")
                print(cfg.to_text(), end="\n\n")

        return Cfg(cfg, checks=checks)

    # returns (accepted,texTree,leftDeriv)
    def simulate(self, i:str):
        l = [c for c in i]
        accepted = self.cfg.contains(l)
        r = ([],[])
        if accepted:
            forr = self.cfg.get_cnf_parse_tree(l)
            r = (self.ablForest(forr, 0), forr.get_leftmost_derivation())
        self.ts.append((i,r[0],r[1]))
        if self.cyk_on_sim:
            self.cyk(i)
        return accepted,[],r[1]

    def toTikz(self, f) -> bool:
        # preamble
        print(r"\documentclass[varwidth=true,multi=page, border=1cm]{standalone}", file=f)
        print(r"\usepackage{forest}", file=f)
        print(r"\usepackage{array}", file=f)
        print(r"\newcommand{\spaceAbl}{3ex}", file=f)
        print(r"\begin{document}", file=f)
        print(r"\begin{page}"+"\nKontextfreie Grammatik:\n\n"+r"$\begin{array}{r!{\to}l}", file=f)
        for prod in self.cfg.productions:
            if prod.body == []:
                print(prod.head.value, "&" , r"\$", r"\\", file=f)
            else:
                print(prod.head.value, "&" , " ".join(list(map(lambda x: x.value, prod.body))), r"\\", file=f)
        print(r"\end{array}$\end{page}", file=f)
        for string,tree,derivation in self.ts:
            print(r"\begin{page}", file=f)
            print("Wort: " + string + "\n", file=f)
            print(r"{\centering\begin{forest}", file=f)
            print(r"where n children=0{fill=pink,rectangle,draw}{}", file=f)
            print("[", file=f)
            for l in tree:
                print(l, file=f)
            print("]", file=f)
            print(r"\end{forest}\par}\vspace*{\spaceAbl}" + "\n\nLinksableitung:\n", file=f)
            for d in derivation:
                print(str(d).replace("#", "-") + r"\\[0cm]", file=f)
            print(r"\end{page}", file=f)
        print(r"\end{document}", file=f)
        return True

    def ablForest(self,tree:ParseTree, lvl:int):
        acc = []
        acc.append(str(tree.value).replace("#", "-"))
        for s in tree.sons:
            acc.append("    "*lvl + "[")
            acc += self.ablForest(s, lvl+1)
            acc.append("    "*lvl + "]")
        return acc

    def toDot(self, fi:str) -> bool:
        print("cfg does no toDot()")
        return False

    def cyk_check(self, a, b, cfg):
        ret = []
        for p in cfg.productions:
            if len(p.body) == 2:
                if p.body[0] == a and p.body[1] == b:
                    ret.append(p.head)
        return ret

    def cyk_init(self, a, cfg):
        ret = set()
        for p in cfg.productions:
            if len(p.body) == 1:
                if p.body[0] == a:
                    ret.add(p.head)
        return ret

    def cyk(self, s:str):
        cfg = self.cfg.to_normal_form()
        print(cfg.to_text())
        tab = [[Terminal(x) for x in s]]
        new = [[self.cyk_init(x, cfg) for x in y] for y in tab]
        tab = new + tab # tab is the existing table and new is the set of step1 since the elements are simply printed, it is no problem that one contains a set and one only literals
        while len(tab[0])-1 >= 1: # go lines up
            tabNewLine = []
            print()
            self.cyk_tabToString(tab, "Step")
            for i in range(len(tab[0]) - 1): # go over cells
                new = set()
                b_i = 1
                for a,b in zip(tab[-2::-1],tab):
                    cellA = a[i]
                    cellB = b[i+b_i]
                    print("checking:\n a", cellA, "\n b", cellB, end="\n -> ")
                    for ax in cellA:
                        for bx in cellB:
                            new = new.union(self.cyk_check(ax,bx, cfg))
                    print(new)
                    b_i += 1
                tabNewLine.append(new)
            tab = [tabNewLine] + tab
        print("\n")
        self.cyk_tabToString(tab, "Final")
    
    def cyk_tabToString(self, tab, title):
        tableString = [[str(x) for x in y] for y in tab]
        st = SingleTable(tableString, title=title)
        for i in range(len(tab[-1])):
            st.justify_columns[i] = 'center'
        st.inner_row_border=True
        st.inner_heading_row_border=False
        print(st.table)


if __name__ == "__main__":
    c = Cfg.loadYaml("./projects/cykTesting/h71b.yaml", 0)
    print(c.cyk("zszwz"))
    print(c.cfg.contains("abaa"))
