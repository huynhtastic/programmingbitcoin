import socket
import time

from random import randint

from helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
)

NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'
TESTNET_NETWORK_MAGIC = b'\x0b\x11\x09\x07'

class NetworkEnvelope:

    def __init__(self, command, payload, testnet=False):
        self.command = command
        self.payload = payload
        if testnet:
            self.magic = TESTNET_NETWORK_MAGIC
        else:
            self.magic = NETWORK_MAGIC

        def __repr__(self):
            return '{}: {}'.format(self.command.decode('ascii'),
                                  self.payload.hex())

    @classmethod
    def parse(cls, s):
        magic = s.read(4)
        command = s.read(12)
        command = command.strip(b'\x00')
        payload_length = little_endian_to_int(s.read(4))
        checksum = s.read(4)
        payload = s.read(payload_length)
        h256 = hash256(payload)
        if h256[:4] != checksum:
            raise ValueError('Invalid payload: {}, {}'.format(h256[:4], checksum))
        if magic == NETWORK_MAGIC:
            testnet = False
        elif magic == TESTNET_NETWORK_MAGIC:
            testnet = True
        else:
            raise ValueError('Invalid network magic')
        return cls(command, payload, testnet)

    def serialize(self):
        s = self.magic
        s += self.command + b'\x00' * (12 - len(self.command))
        s += int_to_little_endian(len(self.payload), 4)
        h256 = hash256(self.payload)
        s += h256[:4]
        s += self.payload
        return s

class VersionMessage:
    command = b'version'

    def __init__(self, version=70015, services=0, timestamp=None,
                 receiver_services=0,
                 receiver_ip=b'\x00\x00\x00\x00', receiver_port=8333,
                 sender_services=0,
                 sender_ip=b'\x00\x00\x00\x00', sender_port=8333,
                 nonce=None, user_agent=b'/programmingbitcoin:0:1/',
                 latest_block=0, relay=False):
        self.version = version
        self.services = services
        if timestamp is None:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.receiver_services = receiver_services
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.sender_services = sender_services
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        if nonce is None:
            self.nonce = int_to_little_endian(randint(0, 2**64), 8)
        else:
            self.nonce = nonce
        self.user_agent = user_agent
        self.latest_block = latest_block
        self.relay = relay

    def serialize(self):
        s = int_to_little_endian(self.version, 4)
        s += int_to_little_endian(self.services, 8)
        s += int_to_little_endian(self.timestamp, 8)
        s += int_to_little_endian(self.receiver_services, 8)
        s += (b'\x00' * 10) + (b'\xff' * 2) + self.receiver_ip
        s += int_to_little_endian(self.receiver_port, 2)
        s += int_to_little_endian(self.sender_services, 8)
        s += (b'\x00' * 10) + (b'\xff' * 2) + self.sender_ip
        s += int_to_little_endian(self.sender_port, 2)
        s += self.nonce
        s += encode_varint(len(self.user_agent))
        s += self.user_agent
        s += int_to_little_endian(self.latest_block, 4)
        if self.relay:
            s += b'\x01'
        else:
            s += b'\x00'
        return s

class VerAckMessage:
    command = b'verack'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return cls()

    def serialize(self):
        return b''


class SimpleNode:

    def __init__(self, host, port=None, testnet=False, logging=False):
        if port is None:
            port = 18333 if testnet else 8333
        self.testnet = testnet
        self.logging = logging
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.stream = self.socket.makefile('rb', None)

    def send(self, message):
        envelope = NetworkEnvelope(
            message.command, message.serialize(), testnet=self.testnet)
        if self.logging:
            print('sending: {}'.format(envelope))
        self.socket.sendall(envelope.serialize())

    def read(self):
        envelope = NetworkEnvelope.parse(self.stream, testnet=self.testnet)
        if self.logging:
            print('receiving: {}'.format(envelope))
        return envelope

    def wait_for(self, *message_classes):
        command = None
        command_to_class = {m.command: m for m in message_classes}
        while command not in command_to_class.keys():
            envelope = self.read()
            command = envelope.command
            if command == VersionMessage.command:
                self.send(VerAckMessage())
            elif command = PingMessage.command:
                self.send(PongMessage(envelope.payload))
        return command_to_class[command].parse(envelope.stream())

    def handshake(self):
        version = VersionMessage()
        self.send(version)
        self.wait_for(VerAckMessage)
        #verack_received = False
        #version_received = False
        #while not verack_received and not version_received:
        #    message = node.wait_for(VersionMessage, VerAckMessage)
        #    if message.command == VerAckMessage.command:
        #        verack_received = True
        #    else:
        #        version_received = true
        #        node.send(VerAckMessage())

class GetHeadersMessage:
    command = b'getheaders'

    def __init__(self, version=70015, num_hashes=1,
                 start_block=None, end_block=None):
        self.version = version
        self.num_hashes = num_hashes
        if start_block is None:
            raise RuntimeError('a start block is required')
        self.start_block = start_block
        if end_block is None:
            self.end_block = b'\x00' * 32
        else:
            self.end_block = end_block

    def serialize(self):
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(self.num_hashes)
        s += self.start_block[::-1]
        s += self.end_block[::-1]
        return s

class HeadersMessage:
    command = b'headers'

    def __init__(self, blocks):
        self.block = blocks

    @classmethod
    def parse(cls, stream):
        num_headers = read_varint(stream)
        blocks = []
        for _ in range(num_headers):
            blocks.append(Block.parse(stream))
            num_txs = read_varint(stream)
            if num_txs != 0:
                raise RuntimeError('number of txs not 0')
        return cls(blocks)
