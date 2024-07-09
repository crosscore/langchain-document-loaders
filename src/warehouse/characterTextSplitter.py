import os
from docx import Document
from langchain.text_splitter import CharacterTextSplitter
import pandas as pd
from dotenv import load_dotenv
import warnings

load_dotenv()
SEPARATOR = os.getenv('SEPARATOR', '\n\n')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '100'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '20'))

if CHUNK_OVERLAP >= CHUNK_SIZE:
    warnings.warn(f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) is larger than or equal to CHUNK_SIZE ({CHUNK_SIZE}). Setting CHUNK_OVERLAP to CHUNK_SIZE - 1.")
    CHUNK_OVERLAP = CHUNK_SIZE - 1

def preprocess_text(doc):
    page_texts = []
    current_page = 1
    current_text = ""

    for para in doc.paragraphs:
        if 'w:lastRenderedPageBreak' in para._element.xml:
            if current_text:
                page_texts.append((current_page, current_text.strip()))
                current_text = ""
            current_page += 1

        if para.text.strip():  # 空の段落を除外
            current_text += para.text + SEPARATOR

    if current_text:  # 最後のページのテキストを追加
        page_texts.append((current_page, current_text.strip()))

    return page_texts

def process_file(input_file):
    file_name = os.path.basename(input_file)
    file_name_without_ext = os.path.splitext(file_name)[0]

    doc = Document(input_file)
    page_texts = preprocess_text(doc)

    text_splitter = CharacterTextSplitter(
        separator=SEPARATOR,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        keep_separator=False
    )

    data = []
    chunk_num = 1

    for page, text in page_texts:
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            data.append({
                'filename': file_name,
                'chunk_num': chunk_num,
                'chunk_text': chunk.strip(),
                'page': page
            })
            chunk_num += 1

    df = pd.DataFrame(data)
    output_file = f"../data/csv/{file_name_without_ext}.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"処理が完了しました。出力ファイル: {output_file}")

if __name__ == "__main__":
    input_file = "../data/docx/test.docx"
    process_file(input_file)
