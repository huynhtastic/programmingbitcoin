"""
Interested in specific points on an elliptic curve defined by the equation:
y^2 = x^3 + ax + b
"""

class Point:
    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        if self.y**2 != self.x**3 + a * x + b:
            raise ValueError('({}, {}) is not on the curve; \
                             {} != {}'.format(x, y, y**2, self.x**3 +a*x+b))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other
