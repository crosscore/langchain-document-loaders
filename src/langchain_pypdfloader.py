import os
import re
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

input_folder = "../data/input/pdf"
output_folder = "../data/output/csv/pdf"
debug_folder = "../data/debug"

def extract_text_from_pdf(file_path):
    print(f"Processing file: {os.path.basename(file_path)}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return pages

def is_japanese(text):
    return bool(re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf]', text))

def process_pdf_to_dataframe(file_name, pages):
    text_splitter = CharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        separator="\n\n"
    )

    data = []
    chunk_number = 0
    for page in pages:
        page_num = page.metadata['page']
        page_text = page.page_content
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
            pages = extract_text_from_pdf(file_path)

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
