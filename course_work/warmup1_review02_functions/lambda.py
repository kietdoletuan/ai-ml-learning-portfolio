#Lesson Date: 25/12

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



