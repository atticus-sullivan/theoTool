import random
from typing import Callable, Iterable

class Ele:
    def __init__(self, terminals:list[str], checks:list[str]):
        self.terminals = terminals
        self.checks    = checks
    
    def simulate(self, i:str) -> tuple[bool,list,list]:
        raise Exception("super 'simulate' shouldn't be called")
    def toTikz(self, f):
        raise Exception("super 'toTikz' shouldn't be called")
    def tpDot(self, f):
        raise Exception("super 'toDot' shouldn't be called")

    def genRandomWords(self, startLen:int, endLen:int, cntPerLength:Callable[[int],int]):
        for l in range(startLen, endLen):
            for _ in range(cntPerLength(l)):
                string = ""
                for _ in range(l):
                    string += random.choice(self.terminals)
                yield string

    def checkAny(self, words:Iterable[str], checkL:Callable[[str],bool], check:bool):
        bs = []
        for word in words:
            s = self.simulate(word)
            bs.append(s[0])
            if check:
                c = checkL(word)
                if c != s[0]:
                    print("Wrong: ", word, *s)
            else:
                print(word, *s[:-2])

        print("\nStats (eval of automata):")
        print("True", len(list(filter(lambda x: x==True, bs))))
        print("False", len(list(filter(lambda x: x==False, bs))))
