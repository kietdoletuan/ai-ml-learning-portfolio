lst_data = [2, 4, 6, 8, 10, 12]
print(lst_data)

#Quiz 1
for i in lst_data:
    if i % 3 == 0:
        lst_data.remove(i)

print(lst_data)

#Quiz 2
list_to_insert = [6,7,8]

lst_data.extend([1,2,3])

lst_data[3:3] = list_to_insert

print(lst_data)


#Quiz 3:

for idx, value in enumerate(lst_data):
    if value % 2 == 0 or value % 5 == 0:
        lst_data[idx] = 0

print(lst_data)
