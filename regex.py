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
