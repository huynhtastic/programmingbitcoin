from helper import (
    hash256,
    int_to_little_endian,
    little_endian_to_int
)

class Block:

    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        version = little_endian_to_int(s.read(4))
        prev_block = s.read(32)[::-1]
        merkle_root = s.read(32)[::-1]
        timestamp = little_endian_to_int(s.read(4))
        bits = s.read(4)
        nonce = s.read(4)
        return cls(version, prev_block, merkle_root, timestamp, bits, nonce)

    def serialize(self):
        s = int_to_little_endian(self.version, 4)
        s += self.prev_block[::-1]
        s += self.merkle_root[::-1]
        s += int_to_little_endian(self.timestamp, 4)
        s += self.bits
        s += self.nonce
        return s

    def hash(self):
        serial = self.serialize()
        h256 = hash256(serial)
        return h256[::-1]

    def bip9(self):
        return self.version >> 29 == 0b001

    def bip91(self):
        return self.version >> 4 & 1 == 1

    def bip141(self):
        return self.version >> 1 & 1 == 1

    def bits_to_target(self):
        exponent = self.bits[-1]
        coefficient = little_endian_to_int(self.bits[:-1])
        target = coefficient * pow(256, exponent - 3)
        return target

    def difficulty(self):
        min_target = 0xffff * pow(256, 0x1d - 3)
        return min_target / target

    def check_pow(self):
        h256 = hash256(self.serialize())
        work = little_endian_to_int(h256)
        return work < self.target()
