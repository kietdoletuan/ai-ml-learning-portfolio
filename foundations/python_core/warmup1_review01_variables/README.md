## Warmup 01 Review 01 — Advanced Variables, Numeric Types & Expression Optimization

**What it does:** Two scripts. The main script evaluates 12 arithmetic expressions and classifies each result as normal, overflow, underflow, nan, or ZeroDivisionError with a one-line explanation. The stretch goal approximates the derivative of e^x across 7 values of h and detects when float underflow collapses the result to 0.0. While the oter script is a replication of the examples shown in the lecture.

**Dataset:** No external data. 12 hardcoded expressions targeting every float edge case from the lesson.

**Approach:** Python eval() wrapped in try/except to safely catch ZeroDivisionError. Results classified using isinstance() guards before math.isnan() and math.isinf() checks. Derivative approximation uses the formula (f(x+h) - f(x)) / h with true value comparison to compute error per h value.

**Result:** All 12 expressions correctly classified. Derivative converges toward e ≈ 2.718 as h shrinks, then collapses to 0.0 at h = 1e-20 due to float underflow, triggering the WARNING status.
