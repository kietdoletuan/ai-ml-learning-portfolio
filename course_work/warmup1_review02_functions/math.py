#Lesson Date: 25/12

import math

def sigmoid(x):
    return 1 / 1 + (math.exp(-x))

def tanh1(x):
    return math.sinh(x)/math.cosh(x)

def tanh2(x):
    return (math.exp(x) - math.exp(-x))/(math.exp(x)+math.exp(-x))

print(sigmoid(5), tanh1(6), tanh1(6))