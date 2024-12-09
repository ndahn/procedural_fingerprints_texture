import math


class SimplexNoise:
    def __init__(self, seed=1):
        self.grad = [
            [1, 1, 0],
            [-1, 1, 0],
            [1, -1, 0],
            [-1, -1, 0],
            [1, 0, 1],
            [-1, 0, 1],
            [1, 0, -1],
            [-1, 0, -1],
            [0, 1, 1],
            [0, -1, 1],
            [0, 1, -1],
            [0, -1, -1],
        ]
        self.perm = [i & 255 for i in range(512)]

        self.F2 = (math.sqrt(3) - 1) / 2
        self.G2 = (3 - math.sqrt(3)) / 6

        for i in range(255):
            seed = self.hash(i + seed)
            r = seed % (256 - i) + i
            swp = self.perm[i]
            self.perm[i + 256] = self.perm[i] = self.perm[r]
            self.perm[r + 256] = self.perm[r] = swp

    def dot2(self, a, b):
        return a[0] * b[0] + a[1] * b[1]

    def sub2(self, a, b):
        return [a[0] - b[0], a[1] - b[1]]

    def noise2D(self, p):
        s = self.dot2(p, [self.F2, self.F2])
        c = [math.floor(p[0] + s), math.floor(p[1] + s)]
        i = c[0] & 255
        j = c[1] & 255
        t = self.dot2(c, [self.G2, self.G2])

        p0 = self.sub2(p, self.sub2(c, [t, t]))
        o = [1, 0] if p0[0] > p0[1] else [0, 1]
        p1 = self.sub2(self.sub2(p0, o), [-self.G2, -self.G2])
        p2 = self.sub2(p0, [1 - 2 * self.G2, 1 - 2 * self.G2])

        n = 0
        n += max(0, 0.5 - self.dot2(p0, p0)) ** 4 * self.dot2(
            self.grad[self.perm[i + self.perm[j]] % 12], p0
        )
        n += max(0, 0.5 - self.dot2(p1, p1)) ** 4 * self.dot2(
            self.grad[self.perm[i + o[0] + self.perm[j + o[1]]] % 12], p1
        )
        n += max(0, 0.5 - self.dot2(p2, p2)) ** 4 * self.dot2(
            self.grad[self.perm[i + 1 + self.perm[j + 1]] % 12], p2
        )

        return 70 * n

    def hash(self, i):
        i = 1103515245 * ((i >> 1) ^ i)
        h32 = 1103515245 * (i ^ (i >> 3))
        return h32 ^ (h32 >> 16)
