# This Python program implements the following use case:
# Write code to find BinaryGap of a given positive integer

def binary_gap(n):
    if n <= 0:
        raise ValueError("Input must be a positive integer")

    binary_representation = bin(n)[2:]
    max_gap = 0
    current_gap = 0
    found_one = False

    for char in binary_representation:
        if char == '1':
            if found_one:
                max_gap = max(max_gap, current_gap)
            current_gap = 0
            found_one = True
        else:
            current_gap += 1

    return max_gap

# Examples
print(binary_gap(9))    # Binary: 1001, Gap: 2
print(binary_gap(529))  # Binary: 1000010001, Gap: 4
print(binary_gap(20))   # Binary: 10100, Gap: 1
print(binary_gap(15))   # Binary: 1111, Gap: 0
print(binary_gap(32))   # Binary: 100000, Gap: 0