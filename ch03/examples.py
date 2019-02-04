from ecc import FieldElement, Point
prime = 223
a = FieldElement(0, prime)
b = FieldElement(7, prime)
x1 = FieldElement(192, prime)
y1 = FieldElement(105, prime)
x2 = FieldElement(17, prime)
y2 = FieldElement(56, prime)
p1 = Point(x1, y1, a, b)
p2 = Point(x2, y2, a, b)
print(p1+p2)

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


# Exercise 4
p1 = [(192, 105), 2]
p2 = [(143, 98), 2]
p3s = [[(47, 71), i] for i in [2,4,8, 21]]
pts = [p1, p2, *p3s]
for pt in pts:
    point = Point(FieldElement(pt[0][0], prime), FieldElement(pt[0][1], prime), a, b)
    for i in range(pt[1] - 1):
        point = point + point
    print(point)

from ecc import S256Point, N, G
# Exercise 6
P = (0x887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c,
 0x61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34)
point = S256Point(*P)
# signature 1
z = 0xec208baa0fc1c19f708a9ca96fdeff3ac3f230bb4a7ba4aede4942ad003c0f60
r = 0xac8d1c87e51d0d441be8b3dd5b05c8795b48875dffe00b7ffcfac23010d3a395
s = 0x68342ceff8935ededd102dd876ffd6ba72d6a427a3edb13d26eb0781cb423c4
s_inv = pow(s, N-2, N)
u = z * s_inv % N
v = r * s_inv % N
print((u*G + v*point).x.num == r)

# signature 2
z = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
r = 0xeff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c
s = 0xc7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6
s_inv = pow(s, N-2, N)
u = z * s_inv % N
v = r * s_inv % N
print((u*G + v*point).x.num == r)

# signing
from helper import hash256
e = int.from_bytes(hash256(b'my secret'), 'big')  # secret key
z = int.from_bytes(hash256(b'my message'), 'big')  # message
k = 123456789  # random k
r = (k*G).x.num  # intended point
k_inv = pow(k, N-2, N)
s = (z + r*e) * k_inv % N
point = e*G

# Exercise 7
e = 12345
z = int.from_bytes(hash256('Programming Bitcoin!'), 'big')
k = 123456789
r = (k * G).x.num
k_inv = pow(k, N-2, N)
s = (z + r*e) * k_inv % N
