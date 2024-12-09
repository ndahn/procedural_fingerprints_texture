import math
import random


class PerlinNoise:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.gradients = {}
        self.permutation = [i for i in range(256)]
        random.shuffle(self.permutation)
        self.permutation += self.permutation  # Repeat to avoid overflow

    def _get_gradient(self, x, y):
        """Retrieve or generate a random gradient vector for the grid point (x, y)."""
        if (x, y) not in self.gradients:
            angle = random.uniform(0, 2 * math.pi)
            self.gradients[(x, y)] = (math.cos(angle), math.sin(angle))
        return self.gradients[(x, y)]

    def _fade(self, t):
        """Smoothstep function to ease the interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a, b, t):
        """Linear interpolation between a and b."""
        return a + t * (b - a)

    def noise(self, x, y):
        """Generate Perlin noise value for the coordinates (x, y)."""
        # Determine grid cell coordinates
        x0 = int(math.floor(x)) & 255
        y0 = int(math.floor(y)) & 255
        x1 = (x0 + 1) & 255
        y1 = (y0 + 1) & 255

        # Relative coordinates within the cell
        dx = x - math.floor(x)
        dy = y - math.floor(y)

        # Smoothstep interpolation weights
        sx = self._fade(dx)
        sy = self._fade(dy)

        # Get gradient vectors for the corners of the cell
        g00 = self._get_gradient(x0, y0)
        g10 = self._get_gradient(x1, y0)
        g01 = self._get_gradient(x0, y1)
        g11 = self._get_gradient(x1, y1)

        # Compute dot products
        n00 = g00[0] * dx + g00[1] * dy
        n10 = g10[0] * (dx - 1) + g10[1] * dy
        n01 = g01[0] * dx + g01[1] * (dy - 1)
        n11 = g11[0] * (dx - 1) + g11[1] * (dy - 1)

        # Interpolate the dot products
        ix0 = self._lerp(n00, n10, sx)
        ix1 = self._lerp(n01, n11, sx)
        value = self._lerp(ix0, ix1, sy)

        return value


# Example usage of PerlinNoise
if __name__ == "__main__":
    perlin = PerlinNoise(seed=42)

    # Generate and print noise values for a grid of points
    for y in range(10):
        for x in range(10):
            print(f"{perlin.noise(x * 0.1, y * 0.1):.2f}", end=" ")
        print()
