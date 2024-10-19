list1 = [10, 15, 1, 56, 77]
list2 = [45, 10, 48, 36, 12]

results = list(map(lambda x, y: x + y, list1, list2))

print(results)