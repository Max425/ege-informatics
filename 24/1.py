import re

f = open('24_28799.txt').readline()

best_len = 0
best_str = ''

for seq in re.findall(r'[0-9]+', f):
    digits = [int(c) for c in seq]
    left = 0
    current_sum = 0
    for right in range(len(seq)):
        current_sum += digits[right]
        while current_sum > 200:
            current_sum -= digits[left]
            left += 1
        if right - left + 1 > best_len:
            best_len = right - left + 1
            best_str = seq[left:right + 1]

print([best_len, best_str])
