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
