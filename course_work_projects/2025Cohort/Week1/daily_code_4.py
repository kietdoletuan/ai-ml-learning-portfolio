def find_divisible_number(a):
    if a < 1 or not a or isinstance(a, int) != True:
        return "Invalid"    
    
    start = 100
    

    while True:
        start += 1

        if start % a == 0:
            return start
        
print(find_divisible_number(5))
print(find_divisible_number(17))
        