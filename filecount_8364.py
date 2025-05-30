# This Python program implements the following use case:
# Write code to count the number of files in current directory and all its nested sub directories, and print the total count

import os

def count_files_in_directory(directory):
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
    return total_files

if __name__ == "__main__":
    current_directory = os.getcwd()
    total_count = count_files_in_directory(current_directory)
    print("Total number of files:", total_count)