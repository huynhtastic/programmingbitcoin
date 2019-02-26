import socket
from network import NetworkEnvelope, VersionMessage

host = 'testnet.programmingbitcoin.com'
port = 18333

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

stream = sock.makefile('rb', None)
version = VersionMessage()
envelope = NetworkEnvelope(version.command, version.serialize())
socket.sendall(envelope.serialize())
while True:
    new_m = NetworkEnvelope.parse(stream)
    print(new_m)
