# langchain-document-loaders/src/pypdfloader_chunk_num.py

import os
import csv
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

input_folder = "../data/input/pdf"
output_folder = "../data/output/csv/pdf"

def extract_text_from_pdf(file_path):
    print(f"Processing file: {os.path.basename(file_path)}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return [page.page_content for page in pages]

def preprocess_text(text):
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r' +\n', '\n', text)
    return text.strip()

def process_pdf_to_csv(file_name, pages_text):
    text_splitter = CharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        separator="\n\n"
    )

    csv_rows = []
    chunk_number = 0
    for page_num, page_text in enumerate(pages_text, start=1):
        page_text = preprocess_text(page_text)
        print(f"Page {page_num} text length: {len(page_text)}")

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
            csv_rows.append({
                'file_name': file_name,
                'file_type': 'pdf',
                'location': str(page_num),
                'chunk_number': chunk_number,
                'manual': chunk
            })
            chunk_number += 1

    print(f"Total chunks across all pages: {len(csv_rows)}")
    return csv_rows

def write_to_csv(data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['file_name', 'file_type', 'location', 'chunk_number', 'manual'])
        writer.writeheader()
        writer.writerows(data)

def main():
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.pdf'):
            file_path = os.path.join(input_folder, file_name)
            pages_text = extract_text_from_pdf(file_path)

            print(f"Total pages in {file_name}: {len(pages_text)}")

            if not any(pages_text):
                print(f"Warning: No text extracted from {file_name}")
                continue

            csv_data = process_pdf_to_csv(file_name, pages_text)

            if not csv_data:
                print(f"Warning: No chunks created for {file_name}")
                continue

            output_file = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.csv")
            write_to_csv(csv_data, output_file)
            print(f"CSV file created: {output_file}")

if __name__ == "__main__":
    main()
