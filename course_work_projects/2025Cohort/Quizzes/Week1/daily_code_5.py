import math

def find_squared_root(a):
    if a < 0:
        print("Squared root of negative number is invalid")
        return None
    if a == 0:
        return 0
     
    EPSILON = 0.001
    
    n = 0
    x = a

    while abs(x - n) >= EPSILON:
        n = x
        x = n - (n**2 - a)/(n*2)
        
    return x


print(find_squared_root(2))