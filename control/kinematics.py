import math

L1 = 124.75
L2 = 190
L3 = 197

"""
运动学逆解
"""
def ik(r_, theta_, h_):
    l = math.sqrt(r_**2 + (h_ - L1)**2)
    alpha = math.atan2(h_ - L1, r_)
    beta = math.acos((l**2 + L2**2 - L3**2) / (2 * L2 * l))
    _theta1 = theta_
    _theta2 = math.pi / 2 - (alpha + beta)
    _theta3 = math.acos((l**2 - L2**2 - L3**2) / (2 * L2 * L3)) - (alpha + beta)
    return _theta1, _theta2, _theta3

"""
运动学正解
"""
def fk(theta1_, theta2_, theta3_):
    r1 = L2 * math.sin(theta2_)
    alpha = math.pi / 2 - theta2_
    r2 = L3 * math.sin(math.pi - theta2_ - (theta3_ + alpha))
    h1 = L2 * math.cos(theta2_)
    h2 = L3 * math.cos(math.pi - theta2_ - (theta3_ + alpha))
    _r = r1 + r2
    _h = L1 + h1 - h2
    _theta = theta1_
    return _r, _theta, _h
