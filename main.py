import sys
import argparse
from cfg import Cfg
from fa import AutomataRegul
from pda import Pda
from ele import genRandomWords

import config

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

    args = parser.parse_args()

    if args.type in ['fa', 'dfa', 'nfa']:
        ele = AutomataRegul.loadYaml(args.inFile)
        print("regex:", ele.toRegex())
    elif args.type in ['cfg']:
        ele = Cfg.load(args.inFile)
    elif args.type in ['pda']:
        ele = Pda.load(args.inFile)
    else:
        quit(-1)

    if hasattr(config, 'cntPerLength'):
        cntPerLength = config.cntPerLength
    else:
        cntPerLength = lambda l: l

    if args.input:
        print("Enter input, terminate with 'EOF', mostly sent by CTRL+D")
        print("Valid terminal symbols: ", ele.terminals)
        gen = sys.stdin.read().splitlines()
        print()
    elif ele.checks != []:
        gen = ele.checks
    elif hasattr(config, 'genRandomWords'):
        gen = config.genRandomWords(startLen=args.startLen, endLen=args.endLen, cntPerLength=cntPerLength, terminals=ele.terminals)
    else:
        gen = genRandomWords(startLen=args.startLen, endLen=args.endLen, cntPerLength=cntPerLength, terminals=ele.terminals)

    if args.check:
        if hasattr(config, 'checkL'):
            checkL = config.checkL
        else:
            raise Exception("checkL not implemented")
    else:
        checkL = lambda _: True # function is not relevant if check is not set
    ele.checkAny(gen,checkL=checkL, check=args.check)

    if args.outBase == "-":
        quit(0)
    elif args.outBase == "+":
        f = sys.stderr
    else:
        ele.toDot(args.outBase+".dot")
        f = open(args.outBase+".tex", "w")
    ele.toTikz(f=f)
    f.close()
