import math


lst_can = ['Canh', 'Tân', 'Nhâm', 'Quý', 'Giáp', 'Ất', 'Bính', 'Đinh','Mậu','Kỷ']
lst_chi = ['Thân', 'Dậu', 'Tuất', 'Hợi','Tí','Sửu','Dần', 'Mão', 'Thìn', 'Tị', 'Ngọ', "Mùi"]

#Quiz 1

def calculate_can_chi_calendar(year):
    can_index = year % 10
    chi_index = year % 12
    print(lst_can[can_index] + " " + lst_chi[chi_index])

calculate_can_chi_calendar(2026)    

print("\n" + "-" * 50 + "\n")

#Quiz 2
def ReLU(x):
    if x > 0:
        print(x)
    else:
        print(0)

def LeakyReLU(x, alpha=0.01):
    if x > 0:
        print(x)
    else:
        print(alpha * x)

def Tanh(x):
    ex = math.exp(x)
    enx = math.exp(-x)
    if ex + enx != 0:
        return (ex - enx) / (ex + enx)
    else:
        return 0

def Sigmoid(x):
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    else:
        return math.exp(x) / (1 + math.exp(x))

def ELU(x, alpha=1.0):
    if x > 0:
        return x
    else:
        return alpha * (math.exp(x) - 1)


# Test values
test_values = [-3, -2, 0, 2, 150]

print("Testing activation functions:")
print("\nInput values:", test_values)

print("\nReLU:")
for x in test_values:
    print(f"ReLU({x}) = {ReLU(x)}")

print("\nLeaky ReLU:")
for x in test_values:
    print(f"LeakyReLU({x}) = {LeakyReLU(x)}")

print("\nTanh:")
for x in test_values:
    print(f"Tanh({x}) = {Tanh(x)}")

print("\nSigmoid:")
for x in test_values:
    print(f"Sigmoid({x}) = {Sigmoid(x)}")

print("\nELU:")
for x in test_values:
    print(f"ELU({x}) = {ELU(x)}")