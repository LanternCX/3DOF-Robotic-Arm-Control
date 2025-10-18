import math

"""
从空间直角坐标系转换到柱面坐标系
"""
def xyz2polar(x, y, z):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    return r, theta, z

def polar2xyz(r, theta, h):
    """
    丛柱面坐标系转换到空间直角坐标系
    """
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y, h

def deg2rad(*angles):
    """
    角度制转弧度制
    """
    if len(angles) == 1 and isinstance(angles[0], (tuple, list)):
        angles = angles[0]
    result = tuple(math.radians(a) for a in angles)
    return result[0] if len(result) == 1 else result

def rad2deg(*angles):
    """
    弧度制转角度制
    """
    if len(angles) == 1 and isinstance(angles[0], (tuple, list)):
        angles = angles[0]
    result = tuple(math.degrees(a) for a in angles)
    return result[0] if len(result) == 1 else result



