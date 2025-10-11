import math

"""
从空间直角坐标系转换到柱面坐标系
"""
def xyz2polar(x, y, z):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    return r, theta, z

"""
丛柱面坐标系转换到空间直角坐标系
"""
def polar2xyz(r, theta, h):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y, h

"""
角度制转弧度制
"""
def deg2rad(*angles):
    if len(angles) == 1 and isinstance(angles[0], (tuple, list)):
        angles = angles[0]
    return tuple(math.radians(a) for a in angles)

"""
弧度制转角度制
"""
def rad2deg(*angles):
    if len(angles) == 1 and isinstance(angles[0], (tuple, list)):
        angles = angles[0]
    return tuple(math.degrees(a) for a in angles)


