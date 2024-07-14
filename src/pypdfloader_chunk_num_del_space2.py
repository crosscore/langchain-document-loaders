import os
import re
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

input_folder = "../data/input/pdf"
output_folder = "../data/output/csv/pdf"

def extract_text_from_pdf(file_path):
    print(f"Processing file: {os.path.basename(file_path)}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return pages

def preprocess_text(text):
    # Replace form feed characters and multiple spaces
    text = text.replace('\f', '\n\n').replace('  ', ' ')

    # Process Japanese and English text differently
    if re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf]', text):
        # For Japanese text
        text = re.sub(r'(?<=[^\n])\n(?=[^\n])', '', text)  # Remove single newlines
        text = re.sub(r'\s+', '', text)  # Remove all spaces
    else:
        # For English text
        text = re.sub(r'(?<=[^\n])\n(?=[^\n])', ' ', text)  # Replace single newlines with space
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces

    # Ensure proper paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)

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
        page_num = page.metadata['page']
        page_text = preprocess_text(page.page_content)
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
            df.to_csv(output_file, index=False, quoting=1)  # quoting=1 is QUOTE_ALL
            print(f"CSV file created: {output_file}")

if __name__ == "__main__":
    main()
