#Lesson Date: 12/01

def linear_search(arr, x):
    for i, v in enumerate(arr):
        if v == x:
            return i
    return -1

def find_all_indices(arr, x):
    indices = []
    for i, v in enumerate(arr):
        if v == x:
            indices.append(i)
    
    return indices

def find_first_div_by_3(arr, x):
    for v in arr:
        if v % 3 == 0:
            return v
    
    return None