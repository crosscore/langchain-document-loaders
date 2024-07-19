import os
import json
from langchain_community.document_loaders import PyPDFLoader

input_folder = "../data/input/pdf"
output_json_folder = "../data/output_00/json"
output_txt_folder = "../data/output_00/txt"

def extract_text_from_pdf(file_path):
    loader = PyPDFLoader(file_path)
    return loader.load()

def save_as_json(file_name, pages):
    json_data = []
    for page in pages:
        unified_source = page.metadata['source'].replace('\\', '/')
        json_data.append({
            "page_content": page.page_content,
            "metadata": {
                **page.metadata,
                "source": unified_source
            }
        })

    output_file = os.path.join(output_json_folder, f"{os.path.splitext(file_name)[0]}.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

def save_as_txt(file_name, pages):
    combined_text = "\n\n".join(page.page_content for page in pages)
    output_file = os.path.join(output_txt_folder, f"{os.path.splitext(file_name)[0]}.txt")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_text)

def process_file(file_name):
    file_path = os.path.join(input_folder, file_name)
    pages = extract_text_from_pdf(file_path)

    if not pages:
        print(f"Warning: No text extracted from {file_name}")
        return

    print(f"Processing {file_name}: {len(pages)} pages")

    save_as_json(file_name, pages)
    save_as_txt(file_name, pages)
    print(f"Created JSON and TXT files for {file_name}")

def main():
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.pdf'):
            process_file(file_name)

if __name__ == "__main__":
    main()
