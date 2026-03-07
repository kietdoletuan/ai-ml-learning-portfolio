import math
import string

expressions = [
    "1e400",           # overflow → inf
    "1e-400",          # underflow → 0.0
    "float('inf') - float('inf')",   # nan
    "float('inf') * 0",              # nan
    "0.0 / 0.0",                     # ZeroDivisionError
    "float('inf') / float('nan')",   # nan propagation
    "0.1 + 0.2 == 0.3",              # False (float error)
    "0.2 + 0.2 == 0.4",              # True (errors cancel)
    "4 + 5 * 3 ** 2",               # precedence: 49
    "1 + 4 * 4 % 4 ** 2 > 3 // 2", # precedence chain → False
    "float('inf') + float('inf')",   # inf
    "pow(1, float('inf'))",          # 1 (Python special case)
]

reasons = [
    "Float exceeded max representable value (~1.8e308)",
    "Float too small for binary representation, rounded to 0",
    "Indeterminate form: inf - inf",
    "Indeterminate form: inf * 0",
    "Error by zero",
    "Any operation with nan propagates nan",
    "Float binary approximation errors do not cancel here",
    "Float binary approximation errors happen to cancel here",
    "power first so 9 * 5 + 4 = 49",
    "Resolves to 1>1 -> False",
    "inf + inf = inf, still infinite",
    "1 raised to any power is 1",
]

print(f"{'Expression':<45} {'Result':<20} {'Class':<15} {'Why'}")
print("-" * 110)

for i, expr in enumerate(expressions):
    classification = "NORMAL"
    try:
        result = eval(expr)
        
        if isinstance(result, float) and math.isnan(result):
            classification = "NAN"
       
        elif isinstance(result, float) and math.isinf(result):
            classification = "OVERFLOW"
        
        elif isinstance(result, float) and result == 0.0:
            classification = "UNDERFLOW"


    except ZeroDivisionError:
        result = "ZeroDivisionError"
        classification = "ERROR"    

    print(f"{expr:<45} {str(result):<20} {classification:<15} {reasons[i]}")        


def safe_derivative(f, x, h):
    result = (f(x + h) - f(x)) / h
    status = "SAFE"

    if result == 0.0:
        status = "WARNING — result is 0.0, likely float underflow. h is too small."


    print(f"{h:<15} {result:<40} {abs(f(result-f(x))):<30} {status}")  

def function(x):
    return math.e**x #e^x as an example


print("-" * 110)
print(f"Derivative approximation of e^x at x = 1")
print(f"True value: {function(1)}")
print(f"{'h':<15} {'approximation':<40} {'error':<30} {'Status'}")
print("-" * 110)
for h in [0.5, 0.1, 0.01, 0.001, 1e-7, 1e-15, 1e-20]:
    safe_derivative(function, 1, h)