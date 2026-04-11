#Lesson Date: 05/01

def e_x(x):
    result = 1
    sum = 1
    for i in range(1000):
        sum = sum*(x/(i+1))
        result += sum
    return result

print(e_x(4))

def factorial(n):
    result = 1
    for i in range(n):
        result += result*i

    return result

n=1
print(f"Factorial of {n} is {factorial(n)}")