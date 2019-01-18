"""
Determine which of these points are on the curve y^2 = x^3 + 5x + 7

(2,4)
(-1,-1)
(18,77)
(5,7)
"""

from Point import Point

a = 5
b = 7
points = [(2,4), (-1,-1), (18,77), (5,7)]

for point in points:
    try:
        Point(*point, a, b)
        print('Point {} is on the curve y^2 = x^3 + 5x + 7'.format(point))
    except Exception as err:
        print('Point {} is NOT on the curve'.format(point))
        print('{}: {}'.format(type(err), str(err)))
