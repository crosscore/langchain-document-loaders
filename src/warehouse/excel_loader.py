import json
import glob
import os
from langchain_community.document_loaders import UnstructuredExcelLoader

def process_excel_files(input_dir, output_base_dir):
    json_dir = os.path.join(output_base_dir, "json", "xlsx")
    txt_dir = os.path.join(output_base_dir, "txt", "xlsx")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(txt_dir, exist_ok=True)

    for excel_file in glob.glob(os.path.join(input_dir, "*.xlsx")):
        base_name = os.path.splitext(os.path.basename(excel_file))[0]

        loader = UnstructuredExcelLoader(excel_file, mode="elements")
        data = loader.load()

        all_content = ""
        json_data = []

        for doc in data:
            all_content += doc.page_content + "\n\n"
            json_data.append({
                'page_content': doc.page_content,
                'metadata': doc.metadata
            })

        # Write text content
        text_output = os.path.join(txt_dir, f"{base_name}_content.txt")
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(all_content)

        # Write JSON content
        json_output = os.path.join(json_dir, f"{base_name}_full.json")
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"Processed {excel_file}")
        print(f"Text content saved to {text_output}")
        print(f"Full JSON content saved to {json_output}")
        print()

input_dir = "../data/input/xlsx"
output_base_dir = "../data/output"

process_excel_files(input_dir, output_base_dir)
