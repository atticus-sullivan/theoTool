
automata.yaml
-----------
Required keys:
- "delta": should be a dict with tuple[int,char] -> int, where the tuple is
  encoded as e.g. "(1,'a')" so that it is understood by ast.literal_eval as tuple
- "sigma": should be list[char]
- "states": should be list[int] (only used for tikz, but programm will crash
  before if absent)
- "initial": should be list[int] (apparently this should be only one value and
  up to now only the first value is used)
- "accepting": should be list[int]

Optional keys:
- "check": should be list[str] with a list of strings that are checked
