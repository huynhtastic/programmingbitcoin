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
        if self.x == None and self.y == None:
            return
        if self.y**2 != self.x**3 + a * x + b:
            raise ValueError('({}, {}) is not on the curve; \
                             {} != {}'.format(x, y, y**2, self.x**3 +a*x+b))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError('Points {}, {} are not on the same curve'
                            .format(self, other))
        elif self.x is None:
            return other
        elif self.y is None:
            return self
        elif self.x == other.x:
            return self.__class__(None, None, self.a, self.b)
        elif self != other:
            x1, y1, x2, y2 = (self.x, self.y, other.x, other.y)

            slope = (y2 - y1) / (x2 - x1)
            x3 = (slope ** 2) - x1 - x2
            y3 = slope * (x1 - x3) - y1
            return self.__class__(x3, y3, self.a, self.b)
        elif self == other:
            if self.y == 0 * self.x:
                return self.__class__(None, None, self.a, self.b)

            x1, y1 = (self.x, self.y)
            a = self.a

            slope = (3 * (x1 ** 2) + a) / (2 * y1)
            x3 = (slope ** 2) - (2 * x1)
            y3 = slope * (x1 - x3) - y1
            return self.__class__(x3, y3, self.a, self.b)

    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        else:
            return 'Point({},{})_{}'.format(self.x.num, self.y.num, self.x.prime)
