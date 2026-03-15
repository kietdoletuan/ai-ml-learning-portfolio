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

#Quiz 5 - 