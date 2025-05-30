# This Python program implements the following use case:
# Write code to find BinaryGap of a given positive integer

def binary_gap(n: int) -> int:
    """
    Calculate the maximum binary gap of a positive integer.

    A binary gap is defined as the maximum number of consecutive zeros
    surrounded by ones in the binary representation of the number.

    Parameters:
    n (int): A positive integer.

    Returns:
    int: The length of the longest binary gap.
    """
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
            if found_one:
                current_gap += 1
    
    return max_gap

# Example usage:
print(binary_gap(9))    # Output: 2
print(binary_gap(529))  # Output: 4
print(binary_gap(20))   # Output: 1
print(binary_gap(1))    # Output: 0
print(binary_gap(15))   # Output: 0
print(binary_gap(16))   # Output: 0
print(binary_gap(1041)) # Output: 5