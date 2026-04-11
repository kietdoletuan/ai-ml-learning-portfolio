#Lesson Date: 25/12
import math

status = True

sqr = lambda x: x*x
compare = lambda x: True if x > 10 else False

while status != False:
    print("="*50)
    try:
        x = int(input("Enter a number: "))
    except ValueError as exception:
        print("Invalid input")
        continue
    
    print(f"Square is {sqr(x)} and compare result is {compare(x)}")


def sigmoid(x):
    return 1 / 1 + (math.exp(-x))

def tanh1(x):
    return math.sinh(x)/math.cosh(x)

def tanh2(x):
    return (math.exp(x) - math.exp(-x))/(math.exp(x)+math.exp(-x))

print(sigmoid(5), tanh1(6), tanh1(6))

