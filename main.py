import sys
import argparse
from cfg import Cfg
from fa import AutomataRegul
from pda import Pda
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
    parser.add_argument("--type", "-t", help="Set type of input", choices=['fa', 'dfa', 'nfa', 'cfg', 'pda'], default='fa')
    parser.add_argument("--input", "-i", help="Use stdin as input for checks (input is requested at the beginning, is simulated as batch afterwards)", action='store_true')
    parser.add_argument("--progress", help="Show progrssbar while simulating (only shows progess in terms of amount of words tested, words tested later will most probably teke longer time, since they mostly are longer (at least defaultRandom generated))", action='store_true')
    parser.add_argument("--build", "-b", help="Automatically build the generated tex and dot code (only in combination with a given filename as outBase)", action='store_true')
    parser.add_argument("--verbose", "-v", help="Be more verbose -vv... for even more verbosity (currently up to 2)", action='count', default=0)
    parser.add_argument("--yes", "-y", help="Answer 'yes' to overwrite questions -> programm is non interactive", action='store_true')

    args = parser.parse_args()

    if args.type in ['fa', 'dfa', 'nfa']:
        ele = AutomataRegul.loadYaml(args.inFile, args.verbose)
        print("regex:", ele.toRegex())
    elif args.type in ['cfg']:
        ele = Cfg.load(args.inFile, args.verbose)
    elif args.type in ['pda']:
        ele = Pda.load(args.inFile, args.verbose)
    else:
        quit(-1)

    if hasattr(config, 'cntPerLength'):
        cntPerLength = config.cntPerLength
    else:
        cntPerLength = lambda l: l+1

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
            l += cntPerLength(x)
    else:
        gen = genRandomWords(startLen=args.startLen, endLen=args.endLen, cntPerLength=cntPerLength, terminals=ele.terminals)
        l = 0
        for x in range(args.startLen,args.endLen):
            l += cntPerLength(x)

    if args.check:
        if hasattr(config, 'checkL'):
            checkL = config.checkL
        else:
            raise Exception("checkL not implemented")
    else:
        checkL = lambda _: True # function is not relevant if check is not set
    ele.checkAny(gen,checkL=checkL, check=args.check, l=l, progress=args.progress)

    if args.outBase == "+":
        f = sys.stderr
        ele.toTikz(f=f)
    elif args.outBase == "-":
        pass
    else:
        if not askOverwrite(args.outBase+".tex", args.yes):
            quit(1)
        f = open(args.outBase+".tex", 'w')
        ele.toTikz(f=f)
        f.close()

        if not askOverwrite(args.outBase+".dot", args.yes):
            quit(1)
        dot = ele.toDot(args.outBase+".dot")

        if args.build:
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
