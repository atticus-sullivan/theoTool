language simulator
=================
For usage, check the `-h` flag.

#### Verbosity table
|Num|Effect|
--- | ---
| 0 (default) | no additional info shown |
| 1 | print transitions/productions read by pyformlang |
| 2 | print output of (pdf) build tools |

Tipp: You may use the `config.py` file to speficy `checkL(i:str)` a function to check if a word
should be accepted or not (this can be a function using regexes, a static
dictionary, or whatever you can imagine as long as it takes a string and returns
a boolean (Tipp: a CFG is possible in here too, see comments in `config.py`)).

When checking random words there are some parameters like startLength and
endLength (words with lengths between these two numbers are generated). With the
function `cntPerLength(l:int)` you can specify how many words of a length should
be generated (this can be a mathematical function, a static dict or what ever
you want, as long as it takes an int and returns an int)
This defaults to `l -> l+1` (linear)

The ``genRandomWords(startLen:int, endLen:int, cntPerLength:Callable[[int],int], terminals:list[str]) -> Iterable[str]``
function can be passed through `config.py` too. The function has to return a
`Iterable[str]` if you use the given parameters doesn't matter.

A single word might be tested more than once (keep that in mind when reading the
printed stats). This can be avoided with `-u`, but NO additional words will be
generated (-> sample size reduces). Hint: You can customize the random generator!

**WARNING:** If using the export to tex/dot be carefull, currently there is no
check if the files already exist, they are simply overwritten.

And please don't take the results for granted, as of now, I'm pretty sure this
should work. But there's never complete safety.

**Tipp:** If you want to work with `pyformlang` on your own (since some features
like equivalence testing, conversion or "Schnitt" are not supported (yet)), but
want to reuse your input yaml files, simply load the corresponding module of
this project and work with the `cfg`/`enfa`/`pda` attributes of the
corresponding class.

Requirements
============
Installed packages:
- pyformlang
- pdflatex
- dot (if you experience issues with the engines that are automatically run,
  please let me know)
- python3

Installation
============
Note that there is a `requirements.txt`, which states the python packages
required to run this programm. Install via `pip install -r requirements.txt`


Input files
===========

automata.yaml
-----------
See `exampleFA.yaml` for an example

Required keys:
- `delta`: should be a list of srcState,char,dstState
- `initial`: should be a state
- `accepting`: should be a list of states

Optional keys:
- `check`: should be list[str] with a list of strings that are to be checked


cfg.yaml
--------
See `exampleCFG.yaml` for an example

Required keys:
- `prods`: should be a list of strings, which represent the productions. A
  production should be of the form `"Var -> term Var term | Var term Var | $"`. A
  `$` represents an epsilon, symbols should be separated by a space, terminals
  start with a lower case char and Non-terminals with an upper case char

Optional keys:
- `check`: should be list[str] with a list of strings that are to be checked
  (here no spaces are needed in between the symbols)

Please note that by default the Nonterminal `S` will be the Axiom

pda.yaml
---------
See `example.yaml` for an example
Please note that the PDA will be accepting on empty stack (see #12)

Required keys:
- `prods`: should be a list of tuples based on this template
  `srcState,symbol,stackSymb,dstState,` afterwards as many stackSymbols
  as needed can follow.
- `initial`: the initial state
- `startStack`: stackSymb which is on the Stack from the beginning

Regarding the `tex` template which may be printed on execution: Each loop has a
key `ownLoop=90` this creates a loop which is centered at `90` degrees. Enter
another Number to rotate the loop.

Credits
-------
Credits to [pyformlang](https://github.com/Aunsiels/pyformlang)


If any bugs or questions occure, simply write an issue with the corresponding
template.
Feel free to contribute and resove issues if you want ;)
