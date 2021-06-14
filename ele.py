import random
from typing import Callable, Iterable

# Print iterations progress from https://stackoverflow.com/a/34325723
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def genRandomWords(startLen:int, endLen:int, cntPerLength:Callable[[int,int],int], terminals:list[str]) -> Iterable[str]:
    for l in range(startLen, endLen):
        for _ in range(cntPerLength(l, len(terminals))):
            string = ""
            for _ in range(l):
                string += random.choice(terminals)
            yield string

class Ele:
    def __init__(self, terminals:list[str], checks:list[str]):
        self.terminals = terminals
        self.checks    = checks
    
    def simulate(self, i:str) -> tuple[bool,list,list]:
        raise Exception("super 'simulate' shouldn't be called")
    def toTikz(self, f) -> bool:
        raise Exception("super 'toTikz' shouldn't be called")
    def toDot(self, fi:str) -> bool:
        raise Exception("super 'toDot' shouldn't be called")

    def checkAny(self, words:Iterable[str], checkL:Callable[[str],bool], check:bool, l:int, progress:bool, unique:bool):
        bs = []
        last = True
        uniqueWords = set()
        for j,word in enumerate(words):
            if unique:
                if word in uniqueWords:
                    continue
                uniqueWords.add(word)
            s = self.simulate(word)
            bs.append(s[0])
            if check:
                c = checkL(word)
                if c != s[0]:
                    if progress:
                        print(("" if last else "\n") + "%-135s" % " ".join(map(lambda x:str(x),("Wrong:", word, *s))), end="" if progress else "\n")
                        last = False
                    else:
                        print("%s" % " ".join(map(lambda x:str(x),("Wrong:", word, *s))))
            else:
                if progress:
                    print(("" if last else "\n") + "%-135s" % " ".join(map(lambda x:str(x),(word, *s))), end="" if progress else "\n")
                    last = False
                else:
                    print("%s" % " ".join(map(lambda x:str(x),(word, *s))))
            if progress and j % 10 == 0:
                printProgressBar(j+1,l, suffix="Refers to #checked words")
                last = True

        if progress:
            print("")

        print("\nStats (eval of automata):")
        print("True", len(list(filter(lambda x: x==True, bs))))
        print("False", len(list(filter(lambda x: x==False, bs))))
