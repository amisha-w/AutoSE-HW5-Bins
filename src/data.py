from rows import *
from cols import Col
from utils import *
from constants import *

class DATA:
    def __init__(self, src):
        self.rows = []
        self.cols = None
        
        if type(src) == str:
            csv(src, self.add)
        else:
            for t in src:
                self.add(t)

    def add(self, t):
        '''
        Adds row
        '''
        if self.cols:
            if type(t) == list:
                t = Row(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = Col(t)

    def clone(self, init):
            '''
            Returns clone of data
            '''
            return copy.deepcopy(self)

    def stats(self, what, cols, nPlaces):
        def fun(_, col):
            if what == 'mid':
                val = col.mid()
            else:
                val = col.div()
            return col.rnd(val, nPlaces), col.txt

        return kap(cols or self.cols.y, fun)

    def dist(self, row1, row2, cols=None):
        n, d = 0, 0
        c = cols or self.cols.x

        for col in c:
            n += 1
            d += col.dist(row1.cells[col.at], row2.cells[col.at]) ** options['p']

        return (d/n) ** (1 / options['p'])


    def around(self, row1, rows=None, cols=None):

        if rows is None: rows = self.rows

        def function(row2):
            return {"row": row2, "dist": self.dist(row1, row2, cols)}

        mapped = map(function, rows)
        return sorted(mapped, key=lambda x: x["dist"])

    def half(self, rows=None, cols=None, above=None):
        def dist(row1, row2):
            return self.dist(row1, row2, cols)
        
        def project(row):
            return {'row': row, 'dist': cosine(dist(row, A), dist(row, B), c)}

        rows = rows or self.rows
        some = many(rows, options['Halves'])
        A = above or any(some)
        B = self.around(A, some)[int(options['Far'] * len(rows)) // 1]['row']
        c = dist(A, B)
        left, right = [], []

        for n, _ in enumerate(sorted(list(map(project, rows)), key=itemgetter('dist'))):
            if n < len(rows) // 2:
                left.append(_['row'])
                mid = _['row']
            else:
                right.append(_['row'])
        return left, right, A, B, mid, c

    def cluster(self, rows=None, min=None, cols=None, above=None):
        rows = rows or self.rows
        min = min or (len(rows) ** options['min'])
        cols = cols or self.cols.x
        node = {'data': self.clone(rows)}

        if len(rows) >= 2 * min:
            left, right, node['A'], node['B'], node['mid'], _ = self.half(rows, cols, above)
            node['left'] = self.cluster(left, min, cols, node['A'])
            node['right'] = self.cluster(right, min, cols, node['B'])
        return node

    def better(self, row1, row2):
        s1, s2, ys = 0, 0, self.cols.y
        for col in ys:
            x = col.norm(row1.cells[col.at])
            y = col.norm(row2.cells[col.at])
            s1 -= math.exp(col.w * (x - y) / len(ys))
            s2 -= math.exp(col.w * (y - x) / len(ys))

        return s1 / len(ys) < s2 / len(ys)

    def tree(self, rows=None, min=None, cols=None, above=None):
        rows = rows or self.rows
        min = min or len(rows) ** options['min']
        cols = cols or self.cols.x
        node = {'data': self.clone(rows)}
        
        if len(rows) >= 2 * min:
            left, right, node['A'], node['B'], node['mid'], _ = self.half(rows, cols, above)
            node['left'] = self.tree(left, min, cols, node['A'])
            node['right'] = self.tree(right, min, cols, node['B'])
        return node

    def sway(self):
        data = self

        def worker(rows, worse, above=None):
            if len(rows) <= len(data.rows) ** options['min']:
                return rows, many(worse, options['rest'] * len(rows))
            else:
                l, r, A, B, _, _ = self.half(rows, None, above)
                if self.better(B, A):
                    l, r, A, B = r, l, B, A
                for row in r:
                    worse.append(row)
                return worker(l, worse, A)

        best, rest = worker(data.rows, [])
        return self.clone(best), self.clone(rest)