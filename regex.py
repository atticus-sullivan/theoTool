from pyformlang.regular_expression import Regex
import yaml

from ele import Ele

class RegularExpression(Ele):
    
    def __init__(self, checks:list[str], re:Regex):
        super().__init__(checks=checks, terminals=list(map(lambda x: x.value, re.to_epsilon_nfa().symbols)))
        self.re = re

    @classmethod
    def loadYaml(cls, path:str, verbose:int):
        with open(path, "r") as f:
            d = yaml.safe_load(f.read())


        if 'regex' not in d or not isinstance(d['regex'], str):
            raise ValueError("regex not definex in input or not a string")
        if verbose >= 1:
            print("Regex:", d['regex'])
        re = Regex(d['regex'])

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return RegularExpression(re=re, checks=d['check'])
        return RegularExpression(re=re, checks=[])

    def toTikz(self,f) -> bool:
        print("regex does not toTikz")
        return False
    def toDot(self,f) -> bool:
        print("regex does not toDot")
        return False

    # returns (accepted,[],[])
    def simulate(self, i:str):
        l = [c for c in i]
        return(self.re.accepts(l),[],[])
