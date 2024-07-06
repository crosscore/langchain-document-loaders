import os
from docx import Document
from langchain.text_splitter import CharacterTextSplitter
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
SEPARATOR = os.getenv('SEPARATOR', '\n\n')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '10'))
CHUNK_OVERLAP = min(int(os.getenv('CHUNK_OVERLAP', '10')), CHUNK_SIZE - 1)  # Ensure overlap is less than chunk size

def get_paragraphs_with_page_numbers(doc):
    paragraphs_with_pages = []
    current_page = 1
    for para in doc.paragraphs:
        if 'w:lastRenderedPageBreak' in para._element.xml:
            current_page += 1
        paragraphs_with_pages.append((para.text, current_page))
    return paragraphs_with_pages

def process_file(input_file):
    file_name = os.path.basename(input_file)
    file_name_without_ext = os.path.splitext(file_name)[0]

    doc = Document(input_file)
    paragraphs_with_pages = get_paragraphs_with_page_numbers(doc)

    text_splitter = CharacterTextSplitter(
        separator=SEPARATOR,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    data = []
    chunk_num = 1
    current_chunk = ""
    current_page = 1

    for para_text, page in paragraphs_with_pages:
        current_chunk += para_text + SEPARATOR
        current_page = page

        while len(current_chunk) >= CHUNK_SIZE:
            chunk = text_splitter.split_text(current_chunk[:CHUNK_SIZE + CHUNK_OVERLAP])[0]
            data.append({
                'filename': file_name,
                'chunk_num': chunk_num,
                'chunk_text': chunk.strip(),
                'page': current_page
            })
            chunk_num += 1
            current_chunk = current_chunk[len(chunk) - CHUNK_OVERLAP:]

    # 残りのテキストを処理
    if current_chunk:
        chunks = text_splitter.split_text(current_chunk)
        for chunk in chunks:
            data.append({
                'filename': file_name,
                'chunk_num': chunk_num,
                'chunk_text': chunk.strip(),
                'page': current_page
            })
            chunk_num += 1

    df = pd.DataFrame(data)

    output_file = f"../data/csv/{file_name_without_ext}.csv"
    os.makedirs("../data/csv/", exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"処理が完了しました。出力ファイル: {output_file}")

if __name__ == "__main__":
    input_file = "../data/docx/test.docx"
    process_file(input_file)
