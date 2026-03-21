import random

def random_number_with_condition(total):
    random.seed(0)

    if total < 2 or not total or isinstance(total, int) != True:
        return "Invalid"

    tries = 0

    while True:
        tries += 1

        a = random.randint(1, 20)
        b = random.randint(1, 20)

        if a + b == total:
            break
        
    return tries

print(random_number_with_condition(40))
print(random_number_with_condition(20))
print(random_number_with_condition(35))



    
