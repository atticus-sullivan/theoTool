# from https://github.com/dgilros/TuringNDTMSimulator / https://www.geeksforgeeks.org/multitape-nondeterministic-turing-machine-simulator/
#### 
# NDTM.py: a nondeterministic Turing Machine Simulator 
# Author: David Gil del Rosal (dgilros@yahoo.com) 
#### 

from collections import defaultdict, deque 
  
class Tape: 
    # Constructor. Sets the blank symbol, the 
    # string to load and the position of the tape head 
    def __init__(self, blank, string ='', head = 0): 
        self.blank = blank 
        self.loadString(string, head) 
      
    # Loads a new string and sets the tape head     
    def loadString(self, string, head): 
        self.symbols = list(string) 
        self.head = head 
          
    # Returns the symbol on the current cell, or the blank 
    # if the head is on the start of the infinite blanks 
    def readSymbol(self): 
        if self.head < len(self.symbols): 
            return self.symbols[self.head] 
        else: 
            return self.blank 
          
    # Writes a symbol in the current cell, extending 
    # the list if necessary 
    def writeSymbol(self, symbol): 
        if self.head < len(self.symbols): 
            self.symbols[self.head] = symbol 
        else: 
            self.symbols.append(symbol) 
              
    # Moves the head left (-1), stay (0) or right (1) 
    def moveHead(self, direction): 
        if direction == 'L': inc = -1
        elif direction == 'R': inc = 1
        else: inc = 0
        self.head+= inc 
          
    # Creates a new tape with the same attributes than this 
    def clone(self): 
        return Tape(self.blank, self.symbols, self.head) 
      
    # String representation of the tape 
    def __str__(self): 
        return str(self.symbols[:self.head]) + \
               str(self.symbols[self.head:]) 
      
  
class NDTM: 
    # Constructor. Sets the start and final states and 
    # inits the TM tapes 
    def __init__(self, start, final, blank ='#', ntapes = 1): 
        self.start = self.state = start 
        self.final = final 
        self.tapes = [Tape(blank) for _ in range(ntapes)] 
        self.trans = defaultdict(list) 
  
    # Puts the TM in the start state and loads an input 
    # string into the first tape 
    def restart(self, string): 
        self.state = self.start 
        self.tapes[0].loadString(string, 0) 
        for tape in self.tapes[1:]: 
            tape.loadString('', 0) 
                      
    # Returns a tuple with the current symbols read 
    def readSymbols(self): 
        return tuple(tape.readSymbol() for tape in self.tapes) 
  
    # Add an entry to the transaction table 
    def addTrans(self, state, read_sym, new_state, moves): 
        self.trans[(state, read_sym)].append((new_state, moves)) 
      
    # Returns the transaction that corresponds to the 
    # current state & read symbols, or None if there is not 
    def getTrans(self): 
        key = (self.state, self.readSymbols()) 
        return self.trans[key] if key in self.trans else None
          
    # Executes a transaction updating the state and the 
    # tapes. Returns the TM object to allow chaining     
    def execTrans(self, trans): 
        self.state, moves = trans 
        for tape, move in zip(self.tapes, moves): 
            symbol, direction = move 
            tape.writeSymbol(symbol) 
            tape.moveHead(direction) 
        return self
      
    # Returns a copy of the current TM 
    def clone(self): 
        tm = NDTM(self.start, self.final) 
        tm.state = self.state 
        tm.tapes = [tape.clone() for tape in self.tapes] 
        tm.trans = self.trans        # shallow copy 
        return tm 
          
    # Simulates the TM computation. Returns the TM that 
    # accepted the input string if any, or None. 
    def accepts(self, string): 
        self.restart(string) 
        queue = deque([self]) 
        while len(queue) > 0: 
            tm = queue.popleft() 
            transitions = tm.getTrans() 
            if transitions is None: 
                # there are not transactions. Exit 
                # if the TM is in the final state 
                if tm.state == tm.final: return tm 
            else: 
                # If the transaction is not deterministic 
                # add replicas of the TM to the queue 
                for trans in transitions[1:]: 
                    queue.append(tm.clone().execTrans(trans)) 
                # execute the current transition 
                queue.append(tm.execTrans(transitions[0])) 
        return None
      
    def __str__(self): 
        out = '' 
        for tape in self.tapes: 
            out+= self.state + ': ' + str(tape)
        return out 
      
    # Simple parser that builds a TM from a text file 
    @staticmethod
    def parse(filename): 
        tm = None
        with open(filename) as file: 
            for line in file: 
                spec = line.strip() 
                if len(spec) == 0 or spec[0] == '%': continue
                if tm is None: 
                    start, final, blank, ntapes = spec.split() 
                    ntapes = int(ntapes) 
                    tm = NDTM(start, final, blank, ntapes) 
                else: 
                    fields = line.split() 
                    state = fields[0] 
                    symbols = tuple(fields[1].split(', ')) 
                    new_st = fields[2] 
                    moves = tuple(tuple(m.split(', ')) 
                                  for m in fields[3:]) 
                    tm.addTrans(state, symbols, new_st, moves) 
        return tm 
      
if __name__ == '__main__': 
    # Example TM that performs unary complement 
    tm = NDTM('q0', 'q1', '#') 
    tm.addTrans('q0', ('0', ), 'q0', (('1', 'R'), )) 
    tm.addTrans('q0', ('1', ), 'q0', (('0', 'R'), )) 
    tm.addTrans('q0', ('#', ), 'q1', (('#', 'S'), )) 
    acc_tm = tm.accepts('11011101') 
    if acc_tm: print(acc_tm) 
    else: print('NOT ACCEPTED')
