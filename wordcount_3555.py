# This Python program implements the following use case:
# Write code which takes a command line input of a word doc or docx file and opens it and counts the number of words, and characters in it and prints all

import sys
from docx import Document
import os

def count_words_and_characters(file_path):
    if not os.path.isfile(file_path):
        print("File does not exist.")
        return

    if not file_path.endswith(('.doc', '.docx')):
        print("File is not a Word document.")
        return

    try:
        doc = Document(file_path)
    except Exception as e:
        print(f"Error opening document: {e}")
        return

    word_count = 0
    char_count = 0

    for paragraph in doc.paragraphs:
        text = paragraph.text
        word_count += len(text.split())
        char_count += len(text)

    print(f"Word count: {word_count}")
    print(f"Character count: {char_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
    else:
        count_words_and_characters(sys.argv[1])