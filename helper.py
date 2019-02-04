import hashlib
from unittest import TestSuite, TextTestRunner


def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)

def hash160(s):
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()
