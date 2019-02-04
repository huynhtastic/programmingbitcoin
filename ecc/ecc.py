from random import randint
from unittest import TestCase

class FieldElement:
    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(num, prime-1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        """
        if other is None:
            return True
        return self.num != other.num or self.prime != other.prime
        """
        return not (self == other)

    def __add__(self, other):
        """
        Finite field addition where we use modulo to ensure that the addition
        of two elements in a prime order result in another element within the
        prime order.
        """
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        """
        Finite field subtraction using the same logic and reasoning as above.
        """
        if self.prime != other.prime:
            raise TypeError('Cannot subtract two numbers in different fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        """
        Finite field multiplication using the same logic and reasoning as
        defined in __add__.
        """
        if self.prime != other.prime:
            return TypeError('Cannot multiply two numbers in different fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num=num, prime=self.prime)

    def __pow__(self, exponent):
        """
        Finite field exponentiation using the same logic and reasoning as
        defined in __add__.
        """
        # We don't want to use this anymore since it's less efficient
        # num = (self.num ** exponent) % self.prime

        """
        This implementation doesn't handle negative exponents correctly
        num = pow(self.num, exponent, self.prime)
        """

        """
        This implementation works, but not as efficiently
        n = exponent
        while n < 0:
            n += self.prime - 1
        """
        # We can turn a negative exp into a positive one with moddiv
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        """
        Finite field division using Fermat's Little Theorem to work backwards
        from a modulus division calculation.
        With a being self.num, b being other.num, and p being self.prime:

        (p-1)! % p = (p-1)! * n^(p-1) % p -> 1 = n^(p-1) % p
        b^-1 -> b^-1 *f(1) -> b^-1 *f(b^(p-1)) -> b^(p-2)
        Thus:
        b^-1 = b^(p-2)
        a /f(b) = a *f(b^-1) ->
        a *f(b^(p-2)); this is what we use to define finite field division
        """
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different fields')
        num = (self.num * pow(other.num, self.prime-2, self.prime)) % self.prime
        return self.__class__(num, self.prime)

class FieldElementTest(TestCase):

    def test_ne(self):
        a = FieldElement(2, 31)
        b = FieldElement(2, 31)
        c = FieldElement(15, 31)
        self.assertEqual(a, b)
        self.assertTrue(a != c)
        self.assertFalse(a != b)

    def test_add(self):
        a = FieldElement(2, 31)
        b = FieldElement(15, 31)
        self.assertEqual(a + b, FieldElement(17, 31))
        a = FieldElement(17, 31)
        b = FieldElement(21, 31)
        self.assertEqual(a + b, FieldElement(7, 31))

    def test_sub(self):
        a = FieldElement(29, 31)
        b = FieldElement(4, 31)
        self.assertEqual(a - b, FieldElement(25, 31))
        a = FieldElement(15, 31)
        b = FieldElement(30, 31)
        self.assertEqual(a - b, FieldElement(16, 31))

    def test_mul(self):
        a = FieldElement(24, 31)
        b = FieldElement(19, 31)
        self.assertEqual(a * b, FieldElement(22, 31))

    def test_pow(self):
        a = FieldElement(17, 31)
        self.assertEqual(a**3, FieldElement(15, 31))
        a = FieldElement(5, 31)
        b = FieldElement(18, 31)
        self.assertEqual(a**5 * b, FieldElement(16, 31))

    def test_div(self):
        a = FieldElement(3, 31)
        b = FieldElement(24, 31)
        self.assertEqual(a / b, FieldElement(4, 31))
        a = FieldElement(17, 31)
        self.assertEqual(a**-3, FieldElement(29, 31))
        a = FieldElement(4, 31)
        b = FieldElement(11, 31)
        self.assertEqual(a**-4 * b, FieldElement(13, 31))


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
        elif self.x == other.x and self.y != other.y:
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

    def __rmul__(self, coefficient):
        coef = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result

class ECCTest(TestCase):

    def test_on_curve(self):
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        valid_points = ((192, 105), (17, 56), (1, 193))
        invalid_points = ((200, 119), (42, 99))
        for x_raw, y_raw in valid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            Point(x, y, a, b)
        for x_raw, y_raw in invalid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            with self.assertRaises(ValueError):
                Point(x, y, a, b)

    def test_add(self):
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        # Exercise 2
        s1 = [(170, 142), (60, 139)]
        s2 = [(47, 71), (17, 56)]
        s3 = [(143, 98), (76, 66)]
        ss = [s1, s2, s3]
        for spt in ss:
            print('\n', spt[0], spt[1])
            p1 = Point(FieldElement(spt[0][0], prime), FieldElement(spt[0][1], prime), a, b)
            p2 = Point(FieldElement(spt[1][0], prime), FieldElement(spt[1][1], prime), a, b)
            print(p1+p2)

P = 2**256 - 2**32 - 977

class S256Field(FieldElement):

    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

A = 0
B = 7
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Point(Point):
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)

    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)

    def verify(self, z, sig):
        s_inv = pow(sig.s, N-2, N)
        u = z * s_inv % N
        v = sig.r * s_inv % N
        total = u*G + v*self
        return total.x.num == sig.r


G = S256Point(
     0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
     0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)


class Signature:
    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Signature({:x},{:x})'.format(self.r, self.s)


class PrivateKey:
    def __init__(self, secret):
        self.secret = secret
        self.point = secret * G

    def hex(self):
        return '{:x}'.format(self.secret).zfill(64)

    def sign(self, z):
        k = randint(O, N)
        r = (k * G).x.num
        k_inv = pow(k, N-2, N)
        s = (z + r * self.secret) * k_inv % N
        if s > N/2:
            s = N - s
        return Signature(r, s)
