import hashlib
from unittest import TestSuite, TextTestRunner

SIGHASH_ALL = 1
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def run(test):
    suite = TestSuite()
    suite.addTest(test)
    TextTestRunner().run(suite)

def hash160(s):
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

def hash256(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def encode_base58(s):
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result

def decode_base58(s):
    num = 0
    for c in s:
        num *= 58
        num+= BASE58_ALPHABET.index(c)
    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError('bad address: {} {}'.format(checksum,
                                                     hash256(combined[:-4])[:4]))
    return combined[1:-4]

def p2pkh_script(h160):
    return Script([0x76, 0xa9, h160, 0x88, 0xac])

def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])

def little_endian_to_int(b):
    return int.from_bytes(b, 'little')

def int_to_little_endian(n, length):
    return n.to_bytes(length, 'little')

def read_varint(s):
    """Reads a variable int frmo a stream"""
    i = s.read(1)[0]
    if i == 0xfd:
        # next two bytes are the number of tx_ins
        return little_endian_to_int(s.read(2))
    elif i == 0xfe:
        # four bytes
        return little_endian_to_int(s.read(4))
    elif i == 0xff:
        # eight bytes
        return little_endian_to_int(s.read(8))
    else:
        # anything else is the int
        return i

def encode_varint(i):
    """Encodes an integer as a varint"""
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError('integer too large: {}'.format(i))

def h160_to_p2pkh_address(h160, testnet=False):
    prefix = b'\x6f' if testnet else b'\x00'
    return encode_base58_checksum(prefix + h160)

def h160_to_p2sh_address(h160, testnet=False):
    prefix = b'\xc4' if testnet else b'\x05'
    return encode_base58_checksum(prefix + h160)

def target_to_bits(target):
    raw_bytes = target.to_bytes(32, 'big')
    raw_bytes = raw_bytes.lstrip(b'\x00')
    if raw_bytes[0] > 0x7f:
        exponent = len(raw_bytes) + 1
        coefficient = b'\x00' + raw_bytes[:2]
    else:
        exponent = len(raw_bytes)
        coefficient = raw_bytes[:3]
    new_bits = coefficient[::-1] + bytes([exponent])
    return new_bits
