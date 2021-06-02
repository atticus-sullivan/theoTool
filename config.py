import re
import math
from typing import Callable, Iterable
import random

from pyformlang.cfg import CFG
# only in effect if --check is set
# specifies if a word should be considered as (in)correct
# can help to automatically check an automata
# TIPP: if you'd like to hardcode some words, use a dictionary here, e.g. ret {'aba':True, 'aab':False}
# Things like the commented use of an other CFG to use as check are possible too!

# cfg = None # global variable sp that the cfg doesn't have to be read all the time
def checkL(i:str):
    # global cfg
    # if cfg is None: # initialize cfg if not alread done
    # # productions written as in yaml, prods separated by newline (not in a list like in yaml)
    #     cfg = CFG.from_text("""
    #             S -> S S | a S S b | $
    #         """)
    ret = len(re.findall("ab", i)) == len(re.findall('ba', i))
    # ret = cfg.contains(i)
    return ret

# only in effect if input is generated randomly
# determines how many words should be tested for a given length
# maybe you'd like to choose a linear or a quadratic function
def cntPerLength(l:int) -> int:
    return l+1

# only in effect, if no checks argument is given in the input yaml
# genrates the words that are checked. This is provided, since sometimes the
# default random generator isn't good enough and only wrong words are checked
def genRandomWords(startLen:int, endLen:int, cntPerLength:Callable[[int],int], terminals:list[str]) -> Iterable[str]:
    for l in range(startLen, endLen):
        for _ in range(cntPerLength(l)):
            string = ""
            for _ in range(l):
                string += random.choice(terminals)
            yield string
