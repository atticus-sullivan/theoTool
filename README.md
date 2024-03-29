language simulator
=================
For usage, check the `-h` flag.

Note that symbols are most of the time separated by spaces and that the alphabet
of a language cannot contain `space`,`.`,`|`,`+`,`*`,`(`,`)`,`epsilon` and `$`
(those are interpreted by `pformlang`). Therfore `python` is interpreted as
single symbol whereas `p y t h o n` is interpreted as the word python
concatenated of the single characters/symbols.

#### Verbosity table
|Num|Effect|
--- | ---
| 0 (default) | no additional info shown |
| 1 | print transitions/productions read by pyformlang |
| 2 | print output of (pdf) build tools |

Tipp: You may use the `config.py` file to speficy the `checkL_...(i:str)`
functions to check if a simulation ran sucessfully or not (changed because of
TMs and goto). Check the comments in the example `config.py` to see what the
parameter `s` is about (representing the result of the simulation).
These functions can use regexes, a static
dictionary, or whatever you can imagine as long as it takes a input string, a
tuple (the return of the simulation) and returns a boolean (this bool now
represents if the simulation was successfully).

Tipp: a CFG/... is possible in here too, see comments in `config.py`.

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

re.yaml
--------
See `exampleRE.yaml` for an example

Required keys:
- `regex`: regular expression as string. Operators like `[``]` are not
  interpreted, you'll have to resolve them.

Optional keys:
- `check`: should be list[str] with a list of strings that are to be checked

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
See `example{Pda,PdaFinal}.yaml` for an example

Required keys:
- `prods`: should be a list of tuples based on this template
  `srcState,symbol,stackSymb,dstState,` afterwards as many stackSymbols
  as needed can follow.
- `initial`: the initial state
- `startStack`: stackSymb which is on the Stack from the beginning

Optional keys:
- `check`: should be list[str] with a list of strings that are to be checked
  (here no spaces are needed in between the symbols)
- `accepting`: list of states that should be accepting. If key is omitted, the
  pad will accept on empty stack (default)

Regarding the `tex` template which may be printed on execution: Each loop has a
key `ownLoop=90` this creates a loop which is centered at `90` degrees. Enter
another Number to rotate the loop.

tm.yaml
-------
See `exampleTM.yaml` for an example. Attention: This is not extensively tested.

Required keys:
- `delta`: should be a list of srcState,char,read,write,dstState,movement[R,L,S]
- `initial`: should be a state
- `accepting`: should a state (only one)
- `space`: should be a string representing an empty cell on band

Optional keys:
- `check`: should be list[str] with a list of strings that are to be checked

Movement: R -> **R**ight; L -> **L**eft; S -> **S**tay

Note that the simulator uses one band by default. If you'd like to use more than
one bands, check out the original simulator and/or reach out to me so that this
feature is being implemented to this tool as well.

goto.yaml
-------
See `exampleGOTO.yaml` for an example. Attention: This is not extensively tested.

Required keys:
- `procedure`: should be a dict of label -> commands (explained below)
- `startLbl`: should be the label on which the programm starts
- `inputVar`: should be the name of the variable into which the input is loaded
- `retVar`: should be the name of the variable which is the output
- `insert`: Should be a list of the valid input characters (used in random
  generator)

Optional keys:
- `check`: should be list[str] with a list of strings that are to be checked

Valid commands are:
- var `:=` var/num
- var `=` var/num `+` var/num
- var `=` var/num `-` var/num
- var `=` var/num `*` var/num
- var `=` var/num `div` var/num
- var `=` var/num `mod` var/num
- `if` pred `goto` label
- `goto` label

Where pred might be one of the following:
- var/num `=` var/num
- var/num `!=` var/num
- var/num `>=` var/num
- var/num `<=` var/num
- var/num `<` var/num
- var/num `>` var/num


Testing status:
--------------
I expect the modules based on pyformlang `fa`, `cfg`, `pda` to be good tested.
The library for the `TM`s is copy paste from the Internet but bugs were already
found. The `goto` lib is self-build and not that much tested.

The latter two should be used with caution!!

Credits
-------
Credits to [pyformlang](https://github.com/Aunsiels/pyformlang)
Also to [https://github.com/dgilros/TuringNDTMSimulator](https://github.com/dgilros/TuringNDTMSimulator) for the ndtmSimulation "library"


If any bugs or questions occure, simply write an issue with the corresponding
template.
Feel free to contribute and resove issues if you want ;)
