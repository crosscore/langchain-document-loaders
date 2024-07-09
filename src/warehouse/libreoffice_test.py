import csv
import os
from docx2pdf import convert
from pypdf import PdfReader
import tempfile

def convert_docx_to_pdf(docx_path):
    pdf_path = tempfile.mktemp(suffix='.pdf')
    convert(docx_path, pdf_path)
    return pdf_path

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text())
    return pages

def save_to_csv(pages, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["page", "text"])
        for page_num, page_content in enumerate(pages, 1):
            writer.writerow([page_num, page_content])

def main():
    input_file = "../data/docx/test.docx"
    file_name_without_ext = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"../data/csv/{file_name_without_ext}_pages.csv"

    pdf_path = convert_docx_to_pdf(input_file)
    pages = extract_text_from_pdf(pdf_path)
    save_to_csv(pages, output_file)

    os.remove(pdf_path)  # 一時的なPDFファイルを削除

    print(f"CSVファイルが保存されました: {output_file}")
    print(f"合計 {len(pages)} ページが処理されました。")

if __name__ == "__main__":
    main()
