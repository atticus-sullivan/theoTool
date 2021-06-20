from gotoLib import GOTO
from ele import Ele
import yaml
from functools import partial

class Goto(Ele):
    
    def __init__(self, aut:GOTO, ins:list[str], checks:list[str]):
        super().__init__(terminals=ins, checks=checks)
        self.goto = aut

    def simulate(self, i:str):
        return self.goto.run(i)

    @classmethod
    def loadYaml(cls, path:str, verbose:int):
        with open(path) as f:
            d = yaml.safe_load(f.read())

        if 'startLbl' not in d:
            raise KeyError("startLbl key not defined in input")
        else:
            startLbl = d['startLbl']

        if 'inputVar' not in d:
            raise KeyError("inputVar key not defined in input")
        else:
            inputVar = str(d['inputVar'])

        if 'retVar' not in d:
            raise KeyError("retVar key not defined in input")
        else:
            retVar = str(d['retVar'])

        goto = GOTO(startLbl=startLbl, inputVar=inputVar, retVar=retVar)

        if 'procedure' not in d or not isinstance(d['procedure'], dict):
            raise KeyError("procedure key not defined in input or not a list")
        else:
            if verbose >= 1:
                print("procedures")
            order = {}
            lastLbl = ""
            for l1,d1 in d['procedure'].items():
                order[lastLbl] = l1
                lastLbl = l1
                t = d1.split()
                if len(t) == 5 and t[1] == '=':
                    if t[3] == '+':
                        if verbose >= 1:
                            print("parsed as ADD", t)
                        # x = y + 3
                        goto.addFunction(lbl=l1, func=partial(goto.plus, t[0], t[2], t[4]))
                    elif t[3] == '-':
                        if verbose >= 1:
                            print("parsed as MINUS", t)
                        # x = y - 3
                        goto.addFunction(lbl=l1, func=partial(goto.minus, t[0], t[2], t[4]))
                    elif t[3] == 'div':
                        if verbose >= 1:
                            print("parsed as DIV", t)
                        # x = y div 3
                        goto.addFunction(lbl=l1, func=partial(goto.div, t[0], t[2], t[4]))
                    elif t[3] == 'mod':
                        if verbose >= 1:
                            print("parsed as MOD", t)
                        # x = y mod 3
                        goto.addFunction(lbl=l1, func=partial(goto.mod, t[0], t[2], t[4]))
                    elif t[3] == '*':
                        if verbose >= 1:
                            print("parsed as MUL", t)
                        # x = y * 3
                        goto.addFunction(lbl=l1, func=partial(goto.mul, t[0], t[2], t[4]))
                    else:
                        raise ValueError("Procedure %s was not understood, 1" % str(t))

                elif len(t) == 2 and t[0] == 'goto':
                    goto.addFunction(lbl=l1, func=partial(goto.goto, t[1]))

                elif len(t) == 6 and t[0] == 'if' and t[4] == 'goto':
                    goto.addFunction(lbl=l1, func=partial(goto.ifGoto, lbl=t[5], pred=goto.pred(t[1:4])))

                elif len(t) == 3 and t[1] == ':=':
                    if verbose >= 1:
                        print("parsed as ASSIGNMENT", t)
                    goto.addFunction(lbl=l1, func=partial(goto.assign, t[0], t[2]))
                elif len(t) == 1 and t[0] == 'halt':
                    goto.addFunction(lbl=l1, func=partial(goto.halt))
                else:
                    raise ValueError("Procedure %s was not understood, 1" % str(t))
            goto.specifyOrder(order)
            if verbose >= 1:
                print()

        if 'insert' in d and isinstance(d['insert'], list):
            for c in d['insert']:
                if not isinstance(c, str):
                    raise KeyError("element in insert was not a string")
        else:
            raise KeyError("insert was not defined")

        if 'check' in d and isinstance(d['check'], list):
            for c in d['check']:
                if not isinstance(c, str):
                    raise KeyError("element in check was not a string")
            return Goto(aut=goto, checks=d['check'], ins=d['insert'])

        return Goto(aut=goto, checks=[], ins=d['insert'])
