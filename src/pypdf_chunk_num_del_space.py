import os
import csv
import re
from pypdf import PdfReader
from langchain_text_splitters import CharacterTextSplitter

input_folder = "../data/input/pdf"
output_folder = "../data/output/csv/pdf"

def extract_text_from_pdf(file_path):
    print(f"Processing file: {os.path.basename(file_path)}")
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        pages.append({'page_num': i, 'content': text})
    return pages

def preprocess_text(text):
    # 日本語と英語の文字を含むかどうかをチェック
    has_japanese = bool(re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))

    # 行ごとに処理
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        # 日本語のみの場合、行内の不要なスペースを削除
        if has_japanese and not has_english:
            line = re.sub(r'(?<!\n)\s+(?!\n)', '', line)
        else:
            # 英語を含む場合、行内の複数のスペースを1つに置換
            line = re.sub(r'(?<!\n)\s+(?!\n)', ' ', line)
        processed_lines.append(line)

    # 処理した行を結合
    text = '\n'.join(processed_lines)

    # 複数の改行を2つの改行に置換（段落間の空行を維持）
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def process_pdf_to_csv(file_name, pages):
    text_splitter = CharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        separator="\n\n"
    )

    csv_rows = []
    chunk_number = 0
    for page in pages:
        page_num = page['page_num']
        page_text = preprocess_text(page['content'])
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
            pages = extract_text_from_pdf(file_path)

            print(f"Total pages in {file_name}: {len(pages)}")

            if not pages:
                print(f"Warning: No text extracted from {file_name}")
                continue

            csv_data = process_pdf_to_csv(file_name, pages)

            if not csv_data:
                print(f"Warning: No chunks created for {file_name}")
                continue

            output_file = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.csv")
            write_to_csv(csv_data, output_file)
            print(f"CSV file created: {output_file}")

if __name__ == "__main__":
    main()
