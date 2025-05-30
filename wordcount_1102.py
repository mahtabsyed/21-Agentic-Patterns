# This Python program implements the following use case:
# Write code which takes a command line input of a word doc or docx file and opens it and counts the number of words, and characters in it and prints all

import sys
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

def count_words_and_characters(file_path):
    try:
        doc = Document(file_path)
        text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
        word_count = len(text.split())
        char_count = len(text)
        return word_count, char_count
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None, None
    except PackageNotFoundError:
        print(f"Error: The file '{file_path}' is not a valid .docx file.")
        return None, None
    except Exception as e:
        print(f"Error processing file: {e}")
        return None, None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file.docx>")
        sys.exit(1)

    file_path = sys.argv[1]
    word_count, char_count = count_words_and_characters(file_path)
    if word_count is not None and char_count is not None:
        print(f"Word Count: {word_count}")
        print(f"Character Count: {char_count}")