my_tuple1 = (2,3)
my_tuple2 = (3,6)

#Quiz 1
def sum_product(tuple):
    sum = 0
    product = 1
    
    for i in range(len(tuple)):
        sum += tuple[i]
        product *= tuple[i]
    
    print(f"Sum and product of vector {tuple} is {sum, product}")

sum_product(my_tuple1)
sum_product(my_tuple2)


#Quiz 2 - Bag of Word
corpus = [
    "Tôi thích môn Toán",
    "Tôi thích AI",
    "Tôi thích âm nhạc"
]

data = ' '.join(corpus)

word_list = list(set(data.split()))
word_list.sort()

print(word_list)

def vectorization(string):
    vector = [0] * len(word_list)
    vocabs = string.split()
    for vocab in vocabs:
        if vocab in word_list:
            vector[word_list.index(vocab)] += 1
    
    print(vector)

vectorization("Tôi thích AI thích Toán")

#Quiz 3 - Algorithms On List
lst_data = [1, 1.1, None, 1.4, None, 1.5, None, 2.0]

cache = []
i = 0
while i < len(lst_data):
    if lst_data[i] == None:
        cache.append(i)
    i += 1
    

if len(cache) != 0:
    print(f"First Index of None: {cache[0]} - The List of Indices of None is {cache}")

#Quiz 4 - Interpolation for List (Time Series)
quiz4_list = lst_data.copy()

for idx, value in enumerate(quiz4_list):
    if value == None:
        for i in range(idx,-1,-1):
            if quiz4_list[i] != None:
                quiz4_list[idx] = quiz4_list[i]
                break
print(quiz4_list) 

#Quiz 5 - matrix representation
mat_a = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
mat_b = [
    [2, 4, 6],
    [1, 3, 5],    
    [1, 0, 1]
]

mat_sum = []
mat_sub = []
for i in range(len(mat_a)):
    row_sum = []
    row_sub = []
    for j in range(len(mat_a[i])):
        row_sum.append(mat_a[i][j] + mat_b[i][j])
        row_sub.append(mat_a[i][j] - mat_b[i][j])
    mat_sum.append(row_sum)
    mat_sub.append(row_sub)

print(mat_sum)
print(mat_sub)

dot_product = []
for i in range(len(mat_a)):
    cal_dot = []
    for j in range(len(mat_a)):
        sum_dot = 0
        for k in range(len(mat_a)):
            sum_dot += mat_a[i][k] * mat_b[k][j]
        cal_dot.append(sum_dot)
    dot_product.append(cal_dot)
print(dot_product)



#Quiz 6 - stop words 
stop_words = ["I", "love", "and", "to"]
input = "I love AI and listen to music"

result = [c for c in input.split() if c not in stop_words]
print(result)


#Quiz 7 - normalization
def normalize(lst_data):
    max_val = max(lst_data)
    min_val = min(lst_data)
    
    return [(x - min_val)/(max_val - min_val) for x in lst_data]

test_cases = [
    [11, 18, 24, 30, 36],
    [50, 100, 150, 200, 250],
    [3, 5, 7, 9, 11]
]

for i , test in enumerate (test_cases) :
    result = normalize(test)
    print(f" Test {i +1}: {result}")

#Quiz 8 - moving average
def moving_average(lst, k):
    lst
    
test_cases_1 = [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9], 3),
    ([10, 20, 30, 40, 50, 60, 70], 4),
    ([5, 10, 15, 20, 25], 2)
]

for i , test in enumerate (test_cases_1) :
    result = normalize(test)
    print(f" Test {i +1}: {result}")