import os
import re
import fitz
import pandas as pd
from langchain_text_splitters import CharacterTextSplitter

input_folder = "../data/input/pdf"
output_folder = "../data/output/csv/pdf"
debug_folder = "../data/debug"

TEXT_BLOCK = 0

def extract_text_and_page_numbers(file_path):
    print(f"Processing file: {os.path.basename(file_path)}")
    doc = fitz.open(file_path)
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        page_dict = page.get_text('dict')
        text = page.get_text()

        logical_num = None
        for block in reversed(page_dict['blocks']):
            if block['type'] == TEXT_BLOCK:
                for line in reversed(block['lines']):
                    for span in reversed(line['spans']):
                        span_text = span['text'].strip()
                        if span_text.isdigit():
                            # Skip if the number is 4 digits or more
                            if len(span_text) < 4:
                                logical_num = span_text
                                break
                    if logical_num:
                        break
            if logical_num:
                break

        pages.append({
            'page_num': i,
            'logical_num': logical_num if logical_num else '-', # If not found, place a "-"
            'content': text
        })
    doc.close()
    return pages

def preprocess_text(text):
    # Remove form feed characters
    text = text.replace('\f', '')

    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)

    # Replace newlines followed by spaces with just newlines
    text = re.sub(r'\n +', '\n', text)

    # Replace multiple newlines with double newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Join hyphenated words at line breaks
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Remove single newlines within sentences, preserving spaces between words
    text = re.sub(r'(?<=[^\n.。!！?？])\n(?=[^\n])', '', text)

    # Remove spaces before Japanese punctuation
    text = re.sub(r' ([、。，．！？])', r'\1', text)

    # Ensure space after period in English text
    text = re.sub(r'(\.)([A-Za-z])', r'\1 \2', text)

    # Remove leading/trailing whitespace
    return text.strip()

def process_pdf_to_dataframe(file_name, pages):
    text_splitter = CharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        separator="\n\n"
    )

    data = []
    chunk_number = 0
    for page in pages:
        page_num = page['page_num']
        logical_num = page['logical_num']
        page_text = preprocess_text(page['content'])
        print(f"Page {page_num} text length: {len(page_text)}")

        # Debug: Log preprocessed text
        log_preprocessed_text(file_name, page_num, page_text)

        if page_text:
            chunks = text_splitter.split_text(page_text)
            print(f"Page {page_num} chunks: {len(chunks)}")

            if not chunks:
                print(f"Warning: No chunks created for page {page_num}. Using whole page as one chunk.")
                chunks = [page_text]
        else:
            print(f"Warning: Empty text on page {page_num}")
            chunks = []

        for chunk in chunks:
            data.append({
                'file_name': file_name,
                'file_type': 'pdf',
                'location': str(page_num),
                'logical_page_num': logical_num,
                'chunk_number': chunk_number,
                'manual': chunk
            })
            chunk_number += 1

    print(f"Total chunks across all pages: {len(data)}")
    return pd.DataFrame(data)

def write_csv(df, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, quoting=1, quotechar='"', escapechar='\\')

def log_preprocessed_text(file_name, page_num, text):
    os.makedirs(debug_folder, exist_ok=True)
    debug_file = os.path.join(debug_folder, f"{os.path.splitext(file_name)[0]}_preprocessed.txt")
    with open(debug_file, 'a', encoding='utf-8') as f:
        f.write(f"--- Page {page_num} ---\n")
        f.write(text)
        f.write("\n\n")

def main():
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.pdf'):
            file_path = os.path.join(input_folder, file_name)
            pages = extract_text_and_page_numbers(file_path)

            print(f"Total pages in {file_name}: {len(pages)}")

            if not pages:
                print(f"Warning: No text extracted from {file_name}")
                continue

            df = process_pdf_to_dataframe(file_name, pages)

            if df.empty:
                print(f"Warning: No chunks created for {file_name}")
                continue

            output_file = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.csv")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            write_csv(df, output_file)
            print(f"CSV file created: {output_file}")

if __name__ == "__main__":
    main()
