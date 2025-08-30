import math

def sin(x):
    return math.sin(math.radians(x))

def cos(x):
    return math.cos(math.radians(x))

def tan(x):
    return math.tan(math.radians(x))

def cot(x):
    return math.cos(math.radians(x)) / math.sin(math.radians(x))

def asin(x):
    return math.degrees(math.asin(x))

def acos(x):
    return math.degrees(math.acos(x))

def atan(x):
    return math.degrees(math.atan(x))

def acot(x):
    return math.degrees(math.atan(1/x))

def sinh(x):
    return math.sinh(x)

def cosh(x):
    return math.cosh(x)

def tanh(x):
    return math.tanh(x)

def coth(x):
    return math.cosh(x) / math.sinh(x)

def asinh(x):
    return math.asinh(x)

def acosh(x):
    return math.acosh(x)

def atanh(x):
    return math.atanh(x)

def acoth(x):
    return math.atanh(1/x)

def exp(x):
    return math.exp(x)

def log(x):
    return math.log(x)
