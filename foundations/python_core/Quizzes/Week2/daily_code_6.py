lst_data = list(range(1,11))
print(lst_data)
#Quiz 1 - First 5 digits
print(lst_data[0:5])


#Quiz 2
cache = []

for i in lst_data:
    if i % 2 != 0:
        cache.append(i)

print(cache)

#Quiz 3
sum = 0

for i in lst_data:
    sum += i
print(sum)