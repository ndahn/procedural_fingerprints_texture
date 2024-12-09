import turtle


def Translate(x, y):
    return lambda p: [p[0] + x, p[1] + y]


def Scale(s):
    return lambda p: [p[0] * s, p[1] * s]


class Tortoise(turtle.RawTurtle):
    def __init__(self, screen):
        super().__init__(screen)
        self.speed(0)
        self.hideturtle()
        self.ps = [0, 0]
        self.transforms = []
        self.pt = self.ps.copy()
        self.traveled = 0
        self.last_update = 0

    def add_transform(self, t):
        self.transforms.append(t)
        self.jump(self.ps)
        return self

    def apply_transforms(self, p):
        if not self.transforms:
            return p
        pt = p.copy()
        for t in self.transforms:
            pt = t(pt)
        return pt

    def goto(self, x, y=None):
        p = x if isinstance(x, (list, tuple)) else [x, y]
        pt = self.apply_transforms(p)

        if self.isdown() and (self.pt[0] - pt[0]) ** 2 + (self.pt[1] - pt[1]) ** 2 > 4:
            self.goto((self.ps[0] + p[0]) / 2, (self.ps[1] + p[1]) / 2)
            self.goto(p)
        else:
            super().goto(pt[0], pt[1])
            self.ps = p
            self.pt = pt

    def position(self):
        return self.ps

    def jump(self, p):
        self.penup()
        self.goto(p[0], p[1])
        self.pendown()
        self.ps = p
        self.pt = self.apply_transforms(p)

    def save_image(self, filename):
        self.screen.getcanvas().postscript(file=filename)
