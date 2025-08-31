import itertools

factors_count = 3
state_count = 2

# All possible assignments for one observation step
assignments = list(itertools.product(range(state_count), repeat=factors_count))

for a in assignments:
    print(a)