
from typing import Callable


class GOTO:
    
    def __init__(self, startLbl:str, inputVar:str, retVar:str):
        self.vars  = {}
        self.funcs = {}
        self.startLbl = startLbl
        self.startVar = inputVar
        self.retVar = retVar
        self.next = {}

    def accessVar(self, var:str):
        if str(var) not in self.vars:
            self.vars[str(var)] = 0

    def getVal(self, var:str):
        if var.isdigit():
            return int(var)
        self.accessVar(var)
        return self.vars[str(var)]

    def run(self,i:int):
        self.vars = {}
        self.vars[str(self.startVar)] = int(i)
        self.currLbl = self.startLbl
        running = True

        while running:
            # print(self.currLbl, self.vars)
            ex = self.currLbl # don't skip the first proc
            if str(self.currLbl) not in self.next:
                running = False
            else:
                self.currLbl = self.next[str(self.currLbl)]
            if self.funcs[str(ex)]() == 1:
                break;
        return self.getVal(str(self.retVar))

    def specifyOrder(self, nxt:dict):
        self.next = nxt

    def assign(self, var:str, val:str):
        self.accessVar(var)
        self.vars[str(var)] = self.getVal(val)

    # var1 = var2 - var3
    def minus(self, var1:str, var2:str, var3:str):
        self.vars[str(var1)] = self.getVal(var2) - self.getVal(var3)
        return 0

    # var1 = var2 + var3
    def plus(self, var1:str, var2:str, var3:str):
        self.vars[str(var1)] = self.getVal(var2) + self.getVal(var3)
        return 0

    # var1 = var2 // var3
    def div(self, var1:str, var2:str, var3:str):
        self.vars[str(var1)] = self.getVal(var2) // self.getVal(var3)
        return 0

    # var1 = var2 % var3
    def mod(self, var1:str, var2:str, var3:str):
        self.vars[str(var1)] = self.getVal(var2) % self.getVal(var3)
        return 0

    # var1 = var2 * var3
    def mul(self, var1:str, var2:str, var3:str):
        self.vars[str(var1)] = self.getVal(var2) * self.getVal(var3)
        return 0

    def goto(self, lbl:str):
        self.currLbl = lbl
        return 0

    def pred(self,t:list[str]):
        if len(t) != 3:
            raise ValueError("Predicate (%s) has to consist of exactly three tokens" % str(t))
        elif t[1] == '=':
            return lambda: self.getVal(t[0]) == self.getVal(t[2])
        elif t[1] == '!=':
            return lambda: self.getVal(t[0]) != self.getVal(t[2])
        elif t[1] == '<=':
            return lambda: self.getVal(t[0]) <= self.getVal(t[2])
        elif t[1] == '>=':
            return lambda: self.getVal(t[0]) >= self.getVal(t[2])
        elif t[1] == '<':
            return lambda: self.getVal(t[0]) <  self.getVal(t[2])
        elif t[1] == '>':
            return lambda: self.getVal(t[0]) >  self.getVal(t[1])
        else:
            raise ValueError("Predicate (%s) has to be of ['=', '!=', '<', '>', '<=', '>=']" % str(t))

    def ifGoto(self, pred:Callable[[],bool], lbl:str):
        if pred():
            self.goto(lbl)
        else:
            pass
        return 0

    def halt(self):
        return 1

    def addFunction(self, lbl:str, func:Callable):
        if str(lbl) in self.funcs:
            print("Error: Label already defined")
            return -1
        self.funcs[str(lbl)] = func
        return 0
