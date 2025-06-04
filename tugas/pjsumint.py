n = int(input())

if n > 0:
    total = sum(range(1, n + 1))
elif n < 0:
    total = sum(range(-1, n - 1, -1))
else:
    total = 0

print(total)
