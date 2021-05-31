import yaml
from ele import Ele
from pyformlang.cfg import CFG
from pyformlang.cfg.parse_tree import ParseTree

class Cfg(Ele):
    def __init__(self, cfg:CFG, checks:list[str]):
        super().__init__(terminals=list(map(lambda x: x.value, cfg.terminals)), checks=checks)
        self.cfg = cfg
        self.ts = []

    @classmethod
    def load(cls, fi:str):
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
        return accepted,r[0],r[1]

    def toTikz(self, f):
        # preamble
        print(r"\documentclass[varwidth=true,multi=page, border=1cm]{standalone}", file=f)
        print(r"\usepackage{forest}", file=f)
        print(r"\newcommand{\spaceAbl}{3ex}", file=f)
        print(r"\begin{document}", file=f)
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

    def ablForest(self,tree:ParseTree, lvl:int):
        acc = []
        acc.append(str(tree.value).replace("#", "-"))
        for s in tree.sons:
            acc.append("    "*lvl + "[")
            acc += self.ablForest(s, lvl+1)
            acc.append("    "*lvl + "]")
        return acc

    def toDot(self, f):
        print("cfg does no toDot()")
