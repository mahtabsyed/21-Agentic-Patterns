# This Python program implements the following use case:
# Write code which takes as input a word doc or docx file and opens it and counts the number of words, characters and numbers of pages in it and prints all

from docx import Document

def analyze_docx(file_path):
    try:
        doc = Document(file_path)
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    num_words = 0
    num_chars = 0
    num_pages = 0  # docx doesn't directly support page count

    for paragraph in doc.paragraphs:
        text = paragraph.text
        num_words += len(text.split())
        num_chars += len(text)

    # Estimate the number of pages based on characters (assuming 1800 characters per page)
    num_pages = (num_chars // 1800) + 1 if num_chars > 0 else 0

    print(f"Number of words: {num_words}")
    print(f"Number of characters: {num_chars}")
    print(f"Estimated number of pages: {num_pages}")

# Example usage:
# analyze_docx('example.docx')