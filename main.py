import sys

if (3,9) > sys.version_info:
    raise Exception("Python version above or equal 3.9 needed. Please contact via gitea if uprading is no option")

import argparse
from cfg import Cfg
from fa import AutomataRegul
from pda import Pda
from regex import RegularExpression
from tm import Ndtm
from goto import Goto
from ele import genRandomWords
import subprocess
import os

import config

# returns if file should be overwritten
def askOverwrite(f:str, yes:bool) -> bool:
    if not yes and os.path.exists(f):
        print("\nFile",f , "does already exist.")
        resp = input("Overwrite? (y/N) ")
        if resp != "y":
            return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Simulate an CFG/FA with either given or random words. The CFG/FA is read from a YAML file. For a doc on this, see the README.md\nBy default the words are simply simulated and the result is printed. Then some sort of tex code can be printed and dot code is generated (see the parameter).",
            epilog="simply try out '%(prog)s -t cfg exampleCFG.yaml -' or '%(prog)s -t fa exampleFA.yaml -'")
    parser.add_argument("inFile", help="YAML file specifying the automata, see README.md for required/optional values or a grammar file")
    parser.add_argument("outBase", help="file to output the tex/dot code (base.tex, base.tex), '-' to supress output, '+' for stderr (tex only). CFG -> syntax trees; FA -> Automata (positioning in tex has to be made manually, consider dot layouts as example (different layout algos are available in dot))")
    parser.add_argument("--startLen", "-s", help="Minimum length of the words to check [DEFAULT: %(default)s]", nargs='?', type=int, default=1)
    parser.add_argument("--endLen", "-e", help="Maximum length of the words to check [DEFAULT: %(default)s]", nargs='?', type=int, default=5)
    parser.add_argument("--check", "-c", help="Check input words via the 'checkL' function", action='store_true')
    parser.add_argument("--type", "-t", help="Set type of input", choices=['re', 'fa', 'dfa', 'nfa', 'cfg', 'pda', 'tm', 'goto'], default='fa')
    parser.add_argument("--input", "-i", help="Use stdin as input for checks (input is requested at the beginning, is simulated as batch afterwards)", action='store_true')
    parser.add_argument("--progress", help="Show progrssbar while simulating (only shows progess in terms of amount of words tested, words tested later will most probably teke longer time, since they mostly are longer (at least defaultRandom generated))", action='store_true')
    parser.add_argument("--build", "-b", help="Automatically build the generated tex and dot code (only in combination with a given filename as outBase)", action='store_true')
    parser.add_argument("--verbose", "-v", help="Be more verbose -vv... for even more verbosity (currently up to 2)", action='count', default=0)
    parser.add_argument("--yes", "-y", help="Answer 'yes' to overwrite questions -> programm is non interactive", action='store_true')
    parser.add_argument("--unique", "-u", help="Test words only once to get a more expressive stat. Note that NO additional Words are beeing generated (might cause a deadlock) if there are duplicates. The sample size is just smaller.", action='store_true')

    args = parser.parse_args()

    if args.type in ['fa', 'dfa', 'nfa']:
        ele = AutomataRegul.loadYaml(args.inFile, args.verbose)
        print("regex:", ele.toRegex())
        if args.check:
            if hasattr(config, 'checkL_fa'):
                checkL = config.checkL_fa
            else:
                raise Exception("checkL_fa not implemented")
        else:
            checkL = lambda _,_: True # function is not relevant if check is not set
    elif args.type in ['cfg']:
        ele = Cfg.loadYaml(args.inFile, args.verbose)
        if args.check:
            if hasattr(config, 'checkL_cfg'):
                checkL = config.checkL_cfg
            else:
                raise Exception("checkL_cfg not implemented")
        else:
            checkL = lambda _,_: True # function is not relevant if check is not set
    elif args.type in ['pda']:
        ele = Pda.loadYaml(args.inFile, args.verbose)
        if args.check:
            if hasattr(config, 'checkL_pda'):
                checkL = config.checkL_pda
            else:
                raise Exception("checkL_pda not implemented")
        else:
            checkL = lambda _,_: True # function is not relevant if check is not set
    elif args.type in ['re']:
        ele = RegularExpression.loadYaml(args.inFile, args.verbose)
        if args.check:
            if hasattr(config, 'checkL_re'):
                checkL = config.checkL_re
            else:
                raise Exception("checkL_re not implemented")
        else:
            checkL = lambda _,_: True # function is not relevant if check is not set
    elif args.type in ['tm']:
        ele = Ndtm.loadYaml(args.inFile, args.verbose)
        if args.check:
            if hasattr(config, 'checkL_tm'):
                checkL = config.checkL_tm
            else:
                raise Exception("checkL not implemented")
        else:
            checkL = lambda _,_: True # function is not relevant if check is not set
    elif args.type in ['goto']:
        ele = Goto.loadYaml(args.inFile, args.verbose)
        if args.check:
            if hasattr(config, 'checkL_goto'):
                checkL = config.checkL_goto
            else:
                raise Exception("checkL not implemented")
        else:
            checkL = lambda _,_: True # function is not relevant if check is not set
    else:
        quit(-1)

    if hasattr(config, 'cntPerLength'):
        cntPerLength = config.cntPerLength
    else:
        cntPerLength = lambda l, w: l+1

    if args.input:
        print("Enter input, terminate with 'EOF', mostly sent by CTRL+D")
        print("Valid terminal symbols: ", ele.terminals)
        gen = sys.stdin.read().splitlines()
        print()
        l = len(gen)
    elif ele.checks != []:
        gen = ele.checks
        l = len(gen)
    elif hasattr(config, 'genRandomWords'):
        gen = config.genRandomWords(startLen=args.startLen, endLen=args.endLen, cntPerLength=cntPerLength, terminals=ele.terminals)
        l = 0
        for x in range(args.startLen,args.endLen):
            l += cntPerLength(x, len(ele.terminals))
    else:
        gen = genRandomWords(startLen=args.startLen, endLen=args.endLen, cntPerLength=cntPerLength, terminals=ele.terminals)
        l = 0
        for x in range(args.startLen,args.endLen):
            l += cntPerLength(x, len(ele.terminals))

    ele.checkAny(gen,checkL=checkL, check=args.check, l=l, progress=args.progress, unique=args.unique)

    if args.outBase == "+":
        f = sys.stderr
        ele.toTikz(f=f)
    elif args.outBase == "-":
        pass
    else:
        if not askOverwrite(args.outBase+".tex", args.yes):
            quit(1)
        f = open(args.outBase+".tex", 'w')
        tex = ele.toTikz(f=f)
        f.close()

        if not askOverwrite(args.outBase+".dot", args.yes):
            quit(1)
        dot = ele.toDot(args.outBase+".dot")

        if args.build:
            if tex:
                print("Building latex -> pdf")
                if not askOverwrite(args.outBase+".pdf", args.yes):
                    quit(1)
                p = subprocess.Popen(["pdflatex", args.outBase+".tex"], stdout=(None if args.verbose >= 2 else open(os.devnull, "w")))
                p.wait()
            if dot:
                print("Building dot -> pdf")
                for dotEng in ["dot", "neato", "twopi", "circo", "fdp", "sfdp", "osage"]:
                    if not askOverwrite(args.outBase+"."+dotEng+".pdf", args.yes):
                        quit(1)
                    p = subprocess.Popen(["dot", "-o", args.outBase+"."+dotEng+".pdf", "-Tpdf", "-K"+dotEng, args.outBase+".dot"],
                            stdout=(None if args.verbose >= 2 else open(os.devnull, "w")))
                    p.wait()
