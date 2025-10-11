import math

def xyz2polar(x, y, z):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    return r, theta, z

def polar2xyz(r, theta, h):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y, h

def deg2rad(a1, a2, a3):
    return math.radians(a1), math.radians(a2), math.radians(a3)

