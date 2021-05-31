For usage, check the "-h" flag.

Tipp: You may use the `config.py` file to speficy `checkL(i:str)` a function to check if a word
should be accepted or not (this can be a function using regexes, a static
dictionary, or whatever you can imagine as long as it takes a string and returns
a boolean).

When checking random words there are some parameters like startLength and
endLength (words with lengths between these two numbers are generated). With the
function `cntPerLength(l:int)` you can specify how many words of a length should
be generated (this can be a mathematical function, a static dict or what ever
you want, as long as it takes an int and returns an int)
This defaults to a linear function with slope `1`


automata.yaml
-----------
See `exampleFA.yaml` for an example

Required keys:
- "delta": should be a list of srcState,char,dstState
- "initial": should be a state
- "accepting": should be a list of states

Optional keys:
- "check": should be list[str] with a list of strings that are to be checked


cfg.yaml
--------
See `exampleCFG.yaml` for an example

Required keys:
- "prods": should be a list of strings, which represent the productions. A
  production should be of the form "Var -> term Var term | Var term Var | $". A
  `$` represents an epsilon, symbols should be separated by a space, terminals
  start with a lower case char and Non-terminals with an upper case char

Optional keys:
- "check": should be list[str] with a list of strings that are to be checked
  (here no spaces are needed in between the symbols)


Credits
-------
Credits to [pyformlang](https://github.com/Aunsiels/pyformlang)
