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

import re
import math
from typing import Callable, Iterable
import random
import itertools

from pyformlang.cfg import CFG
# only in effect if --check is set
# specifies if a word should be considered as (in)correct
# can help to automatically check an automata
# TIPP: if you'd like to hardcode some words, use a dictionary here, e.g. ret {'aba':True, 'aab':False}
# Things like the commented use of an other CFG to use as check are possible too!

def abEx(i:str):
    ret = len(re.findall("ab", i)) == len(re.findall('ba', i))
    return ret

cfg = CFG.from_text("S -> a b")
def cfgContain(i:str):
    return cfg.contains(i)


# s : (accepted:bool,[],[])
def checkL_fa  (i:str, s:tuple) -> bool:
    if 'a' in i and s[0] is True:
        return True
    return False
    # return abEx(i) == s[0]

# s : (True,texTree,linkableitung) or
# s : (False,[],[])
def checkL_pda (i:str, s:tuple) -> bool:
    return cfgContain(i) == s[0]

# s : (True,texTree,linkableitung) or
# s : (False,[],[])
def checkL_cfg (i:str, s:tuple) -> bool:
    return True

# s : (accepted:bool,return of TM lib,[])
# return of TM lib: is a TM (use .tapes to get the tapes and .state to get the final state)
def checkL_tm  (i:str, s:tuple) -> bool:
    return True

# s: (value of the return variable, dict with all variables)
def checkL_goto(i:str, s:tuple) -> bool:
    # checks if the goto programm correctly computes the amount of set bits
    return "{0:b}".format(int(i)).count('1') == s[0]

# s: (accepted:bool,[],[])
def checkL_re  (i:str, s:tuple) -> bool:
    return True

# only in effect if input is generated randomly
# determines how many words should be tested for a given length
# maybe you'd like to choose a linear or a quadratic function
# abs_w represents the amount of terminals that are being tested
def cntPerLength(l:int,abs_w:int) -> int:
    # return cntAll(l, abs_w)
    return cntRand(l)

def cntAll(l:int, abs_w:int) -> int:
    return abs_w**l

def cntRand(l:int) -> int:
    return l+1

# only in effect, if no checks argument is given in the input yaml
# genrates the words that are checked. This is provided, since sometimes the
# default random generator isn't good enough and only wrong words are checked
def genRandomWords(startLen:int, endLen:int, cntPerLength:Callable[[int,int],int], terminals:list[str]) -> Iterable[str]:
    return genAll(startLen, endLen, terminals)
    # return genRand(startLen, endLen, cntPerLength, terminals)

def genAll(startLen:int, endLen:int, terminals:list[str]) -> Iterable[str]:
    for l in range(startLen,endLen):
        rs = itertools.product(*tuple([terminals])*l)
        for r in rs:
            yield "".join(r)

def genRand(startLen:int, endLen:int, cntPerLength:Callable[[int,int],int], terminals:list[str]) -> Iterable[str]:
    for l in range(startLen, endLen):
        for _ in range(cntPerLength(l, len(terminals))):
            s = ""
            for _ in range(l):
                s += random.choice(terminals)
            yield s
