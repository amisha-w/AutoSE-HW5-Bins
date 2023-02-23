import math

class Sym:

    def __init__(self, txt=None, at=None):
        self.n = 0
        self.has = {}
        self.most = 0
        self.mode = None
        if at: self.at = at
        else: self.at = 0
        if txt: self.txt = txt
        else: self.txt = ""


    def add(self, x: str):
        '''
        Method for calculating count of x
        '''
        if x != "?":
            self.n += 1
            if x in self.has:
                self.has[x] = self.has[x] + 1
            else:
                self.has[x] = 1
            if self.has[x] > self.most:
                self.most = self.has[x]
                self.mode = x

    def rnd(self, x, n):
        return x

    def mid(self):
        '''
        Method which returns mode value
        '''
        return self.mode

    def div(self):
        """
        Method which returns standard deviation value
        """
        def FUN(p):
            return p * math.log(p, 2)

        e = 0
        for key, val in self.has.items():
            e += FUN(val / self.n)

        return -e