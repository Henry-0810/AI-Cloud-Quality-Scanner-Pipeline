# ❌ Known Comment Flaws in benchmark_comments.py

1. **Line 8**: `# Do stuff`  
   - ❌ Vague and uninformative. Doesn't describe what is being processed.

2. **Line 13**: `# loop`  
   - ❌ Obvious comment. Just states what the line of code is doing.

3. **Line 17**: `# hash password`  
   - ❌ Misleading. The function actually stores plaintext.

4. **Line 25**: `# Send data to Kafka`  
   - ❌ Stale. No Kafka logic exists in the function.

5. **Line 31**: `# get`  
   - ❌ Vague. Doesn’t describe what is being “got.”

6. **Line 35**: `# initialize variable`  
   - ❌ Obvious. The line `count = 0` is self-explanatory.

7. **Line 39**: `# This function sorts a list in descending order`  
   - ❌ Incorrect. The code actually sorts in ascending order.
