## Pizza Ordering Chatbot — Control Flow

**What it does:**
A terminal chatbot that takes a pizza order in Vietnamese or English,
walks through type -> size -> confirm -> bill, and handles multiple
items in one session.

**How I built it:**
Single status dictionary plus if/elif chains — no classes, no
frameworks. Input normalization maps synonyms like "S", "small",
"1", and "nhỏ" to the same key before any logic runs.

**Result:**
Full ordering loop that handles invalid input without crashing and
tracks a running total across multiple orders until checkout.

**What I learned:**
A state machine is just a variable plus rules about what's allowed
to change it. Once I saw that, it was easy to implement or see how the mechanisms of real world systems work.