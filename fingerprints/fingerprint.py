from typing import Literal
import math
import random

from simplex_noise import SimplexNoise
from perlin_noise import PerlinNoise
from poisson_disc_grid import PoissonDiscGrid


class Fingerprint:
    def __init__(
        self,
        canvas_w,
        canvas_h,
        seed=3,
        radius=1.6,
        pole_distance_cutoff=50,
        global_flow_strength=0.1,
        global_flow_scale=0.01,
        max_path_length=70,
        max_tries=1000,
    ):
        self.simplex = SimplexNoise(seed)
        self.perlin = PerlinNoise(seed)
        self.grid = PoissonDiscGrid(radius)
        self.original_seed = seed
        self.seed = seed
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.radius = radius
        self.pole_distance_cutoff = pole_distance_cutoff
        self.global_flow_strength = global_flow_strength
        self.global_flow_scale = global_flow_scale
        self.max_path_length = max_path_length
        self.max_tries = max_tries

        self.frequency = self.random(2, 4)
        self.yGradient = self.random(0.02, 0.07)

        self.poles = []

    def add_pole(self, x, y, strength, falloff="linear"):
        self.poles.append({"x": x, "y": y, "strength": strength, "falloff": falloff})

    def add_random_poles(
        self,
        num_poles=20,
        min_pole_strength=0,
        max_pole_strength=50,
        falloff: Literal["linear", "quadratic", "logarithmic", "logistic"] = "logistic",
    ):
        for _ in range(num_poles):
            self.add_pole(
                self.random(-self.canvas_w / 5, self.canvas_w / 5),
                self.random(-self.canvas_h / 5, self.canvas_h / 5),
                self.random(min_pole_strength, max_pole_strength),
                falloff,
            )

    def hash(self):
        self.seed += 12345
        r = 1103515245 * ((self.seed >> 1) ^ self.seed)
        r = 1103515245 * (r ^ (r >> 3))
        r = r ^ (r >> 16)
        mod = 1 << 20
        return (r % mod) / mod

    def random(self, min_val, max_val):
        v = self.hash()
        return v * min_val + (1 - v) * max_val

    def fbm(self, x, y):
        # Base value influenced by yGradient
        v = self.yGradient * y

        # Sum the contributions of all poles
        for pole in self.poles:
            distance = math.hypot(x + pole["x"], y + pole["y"])
            if distance > self.pole_distance_cutoff:
                continue

            falloff = pole["falloff"]
            if falloff == "linear":
                div = 3.0 + 0.3 * distance 
            elif falloff == "quadratic":
                div = 3.0 + 0.3 * distance * distance
            elif falloff == "logarithmic":
                div = 3.0 + 0.3 * math.log(distance + 1.0)
            elif falloff == "logistic":
                div = 3.0 + math.exp(-0.3 * (distance - self.pole_distance_cutoff / 4))
            
            v += pole["strength"] / div

        # Apply frequency scaling and noise layers
        x *= self.frequency / 1000
        y *= self.frequency / 1000
        f = 1.0
        for _ in range(3):
            v += self.simplex.noise2D([x * f, y * f]) / f
            f *= 2
            x += 31
        return v

    def global_flow(self, x, y):
        """Noise-based global flow direction based on position (x, y)."""
        # Scale the position for noise input
        # noise_value = self.simplex.noise2D([x * self.global_flow_scale, y * self.global_flow_scale])
        noise_value = self.perlin.noise(
            x * self.global_flow_scale, y * self.global_flow_scale
        )

        # Map the noise value to an angle between 0 and 2π
        angle = noise_value * 2 * math.pi

        # Return the directional vector based on the angle
        return [math.cos(angle), math.sin(angle)]

    def curl_noise(self, x, y):
        eps = 0.01

        curl = [
            (self.fbm(x, y + eps) - self.fbm(x, y - eps)) / (2 * eps),
            (self.fbm(x + eps, y) - self.fbm(x - eps, y)) / (2 * eps),
        ]

        # Get the global flow vector
        global_flow = self.global_flow(x, y)

        # Blend curl noise with the global flow
        blended_vector = [
            (1 - self.global_flow_strength) * curl[0]
            + self.global_flow_strength * global_flow[0],
            (1 - self.global_flow_strength) * curl[1]
            + self.global_flow_strength * global_flow[1],
        ]

        # Normalize the resulting vector
        blended_length = (
            math.hypot(blended_vector[0], blended_vector[1]) / self.radius * 0.99
        )
        return [blended_vector[0] / blended_length, blended_vector[1] / blended_length]

    def draw(self, turtle):
        p = turtle.position()

        curl = self.curl_noise(p[0], p[1])
        dest = [p[0] + curl[0], p[1] + curl[1]]

        if (
            turtle.traveled < self.max_path_length
            and
            # math.hypot(dest[0], dest[1] * 0.7) < 33 + 5 * self.noise.noise2D([p[0] * 0.01, p[1] * 0.01]) and
            self.grid.insert(dest)
        ):
            turtle.goto(dest)
            turtle.traveled += math.hypot(curl[0], curl[1])
        else:
            turtle.traveled = 0
            i = 0
            while i < self.max_tries:
                # This is also defines the area in which the fingerprint will draw
                x, y = max(self.canvas_w / 5, 100), max(self.canvas_h / 5, 100)
                r = [random.uniform(-x, x), random.uniform(-y, y)]
                if self.grid.insert(r):
                    break
                i += 1
            if i >= self.max_tries:
                return False
            turtle.jump(r)

        return True


if __name__ == "__main__":
    from turtle import Screen
    from tortoise import Tortoise, Scale

    # NOTE: for quick previews, reduce canvas size and increase radius. Seed, number of poles,
    # pole strength and global flow parameters influence the appearance of the final texture the most.
    fp = Fingerprint(
        1000,
        1000,
        seed=3,
        radius=1.6,
        pole_distance_cutoff=50,
        global_flow_strength=0.1,
        global_flow_scale=0.01,
        max_path_length=70,
        max_tries=1000,
    )

    fp.add_random_poles(
        num_poles=20,
        min_pole_strength=0,
        max_pole_strength=50,
        falloff="logistic",
    )

    screen = Screen()
    screen.tracer(0, 0)
    screen.screensize(1000, 1000)
    screen.bgcolor("white")

    # Create a turtle for drawing
    turtle = Tortoise(screen)
    turtle.add_transform(Scale(2.5))

    print("Drawing...", end="")
    while fp.draw(turtle):
        pass

    screen.update()
    screen.mainloop()

    filename = f'output_{str(fp.hash()).replace(".", "")}.eps'
    print(f" Done! Saving to {filename}")
    turtle.save_image(filename)
