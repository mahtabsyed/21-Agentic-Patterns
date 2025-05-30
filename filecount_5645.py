# This Python program implements the following use case:
# Write code to count the number of files in current directory and all its nested sub directories, and print the total count

import os
import logging

def count_files_in_directory(directory='.'):
    """
    Count the number of files in the specified directory and its subdirectories.

    Parameters:
    directory (str): The directory path to count files in. Defaults to the current directory.

    Returns:
    int: Total number of files, or None if an error occurs.
    """
    total_files = 0
    try:
        for root, dirs, files in os.walk(directory):
            total_files += len(files)
    except FileNotFoundError:
        logging.error(f"The directory '{directory}' does not exist.")
        return None
    except PermissionError:
        logging.error(f"Permission denied for accessing '{directory}'.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    return total_files

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    total_count = count_files_in_directory()
    if total_count is not None:
        print(f"Total number of files: {total_count}")
    else:
        print("An error occurred while counting files.")