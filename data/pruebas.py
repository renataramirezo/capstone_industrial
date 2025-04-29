set = {frozenset({1,2}),frozenset({2,1}),frozenset({3,4})}
print({2,1} in set)
print(set)

for j in set:
    if 2 in j:
        print('estoy')
    else:
        print('noestoy')