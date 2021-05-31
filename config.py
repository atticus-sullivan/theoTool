import re
import math

# only in effect if --check is set
# specifies if a word should be considered as (in)correct
# can help to automatically check an automata
# TIPP: if you'd like to hardcode some words, use a dictionary here, e.g. ret {'aba':True, 'aab':False}
def checkL(i:str):
    ret = len(re.findall("ab", i)) == len(re.findall('ba', i))
    return ret

# only in effect if input is generated randomly
# determines how many words should be tested for a given length
# maybe you'd like to choose a linear or a quadratic function
def cntPerLength(l:int) -> int:
    return l
