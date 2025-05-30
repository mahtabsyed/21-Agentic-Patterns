# This Python program implements the following use case:
# Write code to count the number of files in current directory and all its nested sub directories, and print the total count

import os

def count_files_in_directory(directory='.'):
    """
    Counts the total number of files in the specified directory and its subdirectories.

    Parameters:
    directory (str): The path to the directory. Defaults to the current directory.

    Returns:
    int: The total number of files.
    """
    if not os.path.isdir(directory):
        print(f"Error: The path '{directory}' is not a directory.")
        return 0

    total_files = 0
    try:
        for root, dirs, files in os.walk(directory):
            total_files += len(files)
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to access '{directory}'.")
    return total_files

if __name__ == "__main__":
    total_count = count_files_in_directory()
    print(f"Total number of files: {total_count}")