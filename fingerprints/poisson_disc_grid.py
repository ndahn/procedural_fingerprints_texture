import math


class PoissonDiscGrid:
    def __init__(self, radius):
        self.cell_size = 1 / math.sqrt(2) / radius
        self.radius2 = radius * radius
        self.cells = {}

    def insert(self, p):
        x = int(p[0] * self.cell_size)
        y = int(p[1] * self.cell_size)

        for xi in range(x - 1, x + 2):
            for yi in range(y - 1, y + 2):
                for existing_point in self.cell(xi, yi):
                    if (existing_point[0] - p[0]) ** 2 + (
                        existing_point[1] - p[1]
                    ) ** 2 < self.radius2:
                        return False

        self.cell(x, y).append(p)
        return True

    def cell(self, x, y):
        if x not in self.cells:
            self.cells[x] = {}
        if y not in self.cells[x]:
            self.cells[x][y] = []
        return self.cells[x][y]
