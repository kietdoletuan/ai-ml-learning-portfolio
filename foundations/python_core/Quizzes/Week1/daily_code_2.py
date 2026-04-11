import math

print("\n" + "-" * 50 + "\n")

#Quiz 1 - Compute Interest
def compute_interest(money, period):
  result = money
  for i in range(1, period):
      result += money / math.factorial(i)

  return result

print(compute_interest(1, 365))

print("\n" + "-" * 25 + "\n")

#Quiz 2 - Eratosthenes
def is_prime_eratosthenes(n):
    
    if not n or isinstance(n, int) != True:
       return "Invalid"
    
    elif n < 2: 
       return False
    
    prime = [True] * (n + 1)
    prime[0] = prime[1] = False

    for i in range(2, int(math.sqrt(n)) + 1):
       if prime[i] == True:
          for idx in range(i**2, n + 1, i):
             prime[idx] = False

    return prime[n]

print(is_prime_eratosthenes(10))


print("\n" + "-" * 50 + "\n")
